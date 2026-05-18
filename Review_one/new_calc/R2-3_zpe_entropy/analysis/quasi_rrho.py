"""
R2-3 — Quasi-RRHO thermochemistry post-processor.

Parses CP2K vibrational-analysis output (*.out) and reports
ZPE, U_T, T*S, and Gibbs free-energy correction G_corr at one
or more temperatures, applying Grimme (2012) quasi-RRHO so that
low-frequency modes (default cutoff 100 cm^-1) are treated as
free-rotor contributions to the entropy.

Usage
-----
    python quasi_rrho.py <cp2k_out> [--T 298.15] [--cutoff 100]
                                    [--ads / --gas]
                                    [--mol-mass <amu>] [--I A B C]

Notes
-----
* For adsorbed states, --ads (default) skips translational and
  rotational contributions (only ZPE, U_vib, S_vib, S_vib quasi).
* For gas-phase reference molecules, --gas adds ideal-gas
  translational (Sackur-Tetrode) and rotational entropy. Pass
  the molecular mass (amu) and the principal moments of inertia
  (amu * A^2) via --I; for linear molecules pass two A=B and C=0.
* All output is in eV.
* The script DOES NOT consume CP2K's printed S_vib directly;
  it re-derives entropy from the printed frequencies so the
  Grimme cutoff can be applied.

References
----------
* Grimme, S.  Chem. Eur. J. 2012, 18, 9955-9964.
  doi:10.1002/chem.201200497  (quasi-RRHO cutoff function)
* McQuarrie, Statistical Mechanics, 2000  (ideal-gas RRHO).
"""
from __future__ import annotations
import argparse
import math
import re
import sys
from pathlib import Path

# ---- physical constants ----------------------------------------------------
H_PLANCK_SI = 6.62607015e-34       # J s
HBAR_SI     = 1.054571817e-34      # J s
K_BOLTZ_SI  = 1.380649e-23         # J / K
N_A         = 6.02214076e23
R_GAS       = 8.31446261815324     # J / mol / K
C_LIGHT_SI  = 2.99792458e10        # cm / s

EV_PER_J    = 1.0 / 1.602176634e-19
EV_PER_HARTREE = 27.211386245988

# ---- CP2K parsing ----------------------------------------------------------
FREQ_LINE_RE = re.compile(r"^\s*VIB\|Frequency\s*\(cm-1\)\s+([\-\d\.\sE]+)$")
ALT_FREQ_RE  = re.compile(r"^\s+(\-?\d+\.\d+)\s+(\-?\d+\.\d+)\s+(\-?\d+\.\d+)$")


def parse_frequencies_cm1(out_path: Path) -> list[float]:
    """Pull harmonic frequencies (cm-1) from a CP2K vibrational-analysis .out."""
    freqs: list[float] = []
    in_block = False
    with out_path.open() as f:
        for line in f:
            if "NORMAL MODES" in line or "VIB|" in line:
                in_block = True
            if in_block:
                m = re.match(r"^\s*VIB\|Frequency\s*\(cm-1\)\s+(.+)$", line)
                if m:
                    parts = m.group(1).split()
                    for p in parts:
                        try:
                            v = float(p)
                            freqs.append(v)
                        except ValueError:
                            pass
                if line.strip().startswith("ROT|") or line.strip().startswith("TRANS|"):
                    break
    return freqs


# ---- thermochemistry -------------------------------------------------------
def harmonic_zpe_eV(freqs_cm1: list[float]) -> float:
    """Sum of (1/2) h nu over real modes only."""
    total = 0.0
    for v in freqs_cm1:
        if v <= 0.0:
            continue
        nu_hz = v * C_LIGHT_SI                      # convert cm-1 to Hz
        total += 0.5 * H_PLANCK_SI * nu_hz          # J
    return total * EV_PER_J


def harmonic_U_vib_eV(freqs_cm1: list[float], T: float) -> float:
    """Vibrational thermal energy U_vib(T) excluding ZPE."""
    total = 0.0
    if T <= 0.0:
        return 0.0
    for v in freqs_cm1:
        if v <= 0.0:
            continue
        nu_hz = v * C_LIGHT_SI
        x = H_PLANCK_SI * nu_hz / (K_BOLTZ_SI * T)
        total += K_BOLTZ_SI * T * x / (math.exp(x) - 1.0)
    return total * EV_PER_J


def harmonic_S_vib_per_mode(nu_hz: float, T: float) -> float:
    """S_vib (J / K) for one harmonic mode at temperature T."""
    if nu_hz <= 0.0 or T <= 0.0:
        return 0.0
    x = H_PLANCK_SI * nu_hz / (K_BOLTZ_SI * T)
    return K_BOLTZ_SI * (x / (math.exp(x) - 1.0) - math.log(1.0 - math.exp(-x)))


def free_rotor_S_per_mode(nu_hz: float, T: float, mu_inertia: float) -> float:
    """Free-rotor entropy approximation for one mode (J / K).

    Grimme 2012, eq 6: treats a low-frequency vibrational mode as
    a rotation of moment of inertia mu, related to the harmonic
    frequency by mu = h / (8 pi^2 nu).
    """
    if nu_hz <= 0.0 or T <= 0.0:
        return 0.0
    mu_prime = mu_inertia * 1.0e-46 / (mu_inertia + 1.0e-46)   # damping (ignored here, see Grimme)
    arg = (8.0 * math.pi**3 * mu_prime * K_BOLTZ_SI * T) / (H_PLANCK_SI**2)
    if arg <= 0.0:
        return 0.0
    return 0.5 * K_BOLTZ_SI + 0.5 * K_BOLTZ_SI * math.log(arg)


def grimme_qrrho_S_vib(freqs_cm1: list[float], T: float, cutoff_cm1: float = 100.0) -> float:
    """Total vibrational entropy with Grimme's switching to free-rotor below cutoff.

    Returns S_vib in J / K. The damping function w(nu) interpolates
    between harmonic (high nu) and free-rotor (low nu); we use the
    standard Grimme form w = 1 / (1 + (cutoff/nu)^4).
    """
    total = 0.0
    for v in freqs_cm1:
        if v <= 0.0:
            continue
        nu_hz = v * C_LIGHT_SI
        S_har = harmonic_S_vib_per_mode(nu_hz, T)

        # moment of inertia for free-rotor approximation (Grimme eq 4)
        mu = H_PLANCK_SI / (8.0 * math.pi**2 * nu_hz)
        S_fr = free_rotor_S_per_mode(nu_hz, T, mu * 1e46)   # mu kept in SI; scaled in free_rotor

        w = 1.0 / (1.0 + (cutoff_cm1 / v) ** 4)
        total += w * S_har + (1.0 - w) * S_fr
    return total


def ideal_gas_S_trans(mass_amu: float, T: float, P_Pa: float = 101325.0) -> float:
    """Sackur-Tetrode translational entropy (J / K)."""
    if mass_amu <= 0 or T <= 0:
        return 0.0
    m_kg = mass_amu * 1.66053906660e-27
    V = K_BOLTZ_SI * T / P_Pa
    Lambda = H_PLANCK_SI / math.sqrt(2.0 * math.pi * m_kg * K_BOLTZ_SI * T)
    return K_BOLTZ_SI * (math.log(V / Lambda**3) + 5.0 / 2.0)


def ideal_gas_S_rot(inertia_amu_A2: tuple[float, float, float], T: float, sigma: int) -> float:
    """Rotational entropy (J / K).

    For a linear molecule, pass (I, I, 0). For nonlinear, three
    principal moments. Inputs in amu * A^2.
    """
    if T <= 0:
        return 0.0
    Ia, Ib, Ic = inertia_amu_A2
    Ia_SI = Ia * 1.66053906660e-47          # amu * A^2 -> kg * m^2
    Ib_SI = Ib * 1.66053906660e-47
    Ic_SI = Ic * 1.66053906660e-47
    if Ic_SI <= 0:                          # linear molecule
        # use Ia (assume Ia == Ib for linear)
        T_rot = HBAR_SI**2 / (2.0 * K_BOLTZ_SI * Ia_SI)
        return K_BOLTZ_SI * (math.log(T / (sigma * T_rot)) + 1.0)
    # nonlinear
    arg = math.sqrt(math.pi * (Ia_SI * Ib_SI * Ic_SI)) / sigma
    return K_BOLTZ_SI * (1.5 + math.log(
        (8.0 * math.pi**2 / H_PLANCK_SI**2 * K_BOLTZ_SI * T) ** 1.5 * arg
    ))


# ---- entry point -----------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("out", type=Path, help="CP2K vibrational-analysis .out file")
    ap.add_argument("--T", type=float, default=298.15, help="Temperature (K)")
    ap.add_argument("--cutoff", type=float, default=100.0,
                    help="Grimme quasi-RRHO cutoff in cm-1 (default 100)")
    ap.add_argument("--ads", action="store_true",
                    help="Adsorbed-state: vibrational only (default)")
    ap.add_argument("--gas", action="store_true",
                    help="Gas phase: add trans+rot using --mol-mass and --I and --sigma")
    ap.add_argument("--mol-mass", type=float, default=None, help="Molecular mass in amu (gas only)")
    ap.add_argument("--I", nargs=3, type=float, default=None,
                    help="Three principal moments of inertia in amu*A^2 (gas only)")
    ap.add_argument("--sigma", type=int, default=1, help="Rotational symmetry number (gas only)")
    args = ap.parse_args()

    freqs = parse_frequencies_cm1(args.out)
    if not freqs:
        print(f"ERROR: no frequencies parsed from {args.out}", file=sys.stderr)
        return 2

    imag = [v for v in freqs if v < 0.0]
    real = [v for v in freqs if v >= 0.0]
    print(f"# {args.out}")
    print(f"# total modes: {len(freqs)}, imaginary: {len(imag)}, real: {len(real)}")
    if imag:
        print(f"# WARNING: imaginary frequencies present: {imag}", file=sys.stderr)

    ZPE = harmonic_zpe_eV(real)
    U_vib = harmonic_U_vib_eV(real, args.T)
    S_vib_J = grimme_qrrho_S_vib(real, args.T, cutoff_cm1=args.cutoff)

    # ideal-gas translation + rotation if requested
    S_trans_J = 0.0
    S_rot_J = 0.0
    if args.gas:
        if args.mol_mass is None or args.I is None:
            print("ERROR: --gas requires --mol-mass and --I A B C", file=sys.stderr)
            return 2
        S_trans_J = ideal_gas_S_trans(args.mol_mass, args.T)
        S_rot_J = ideal_gas_S_rot(tuple(args.I), args.T, args.sigma)

    S_total_J = S_vib_J + S_trans_J + S_rot_J
    TS_eV = args.T * S_total_J / 1.602176634e-19      # J -> eV (T*S already in J)

    # H_corr for ideal gas = U_vib + (3/2)kT (trans) + (3/2)kT (rot, nonlinear) or kT (linear) + kT (pV)
    kT_eV = K_BOLTZ_SI * args.T * EV_PER_J
    if args.gas and args.I and args.I[2] > 0:
        H_thermal = U_vib + 1.5 * kT_eV + 1.5 * kT_eV + kT_eV   # 3/2 trans + 3/2 rot + pV
    elif args.gas:
        H_thermal = U_vib + 1.5 * kT_eV + 1.0 * kT_eV + kT_eV   # linear: 3/2 trans + kT rot + pV
    else:
        H_thermal = U_vib                                       # adsorbed: vibrational only

    G_corr = ZPE + H_thermal - TS_eV

    print()
    print(f"T               = {args.T:.2f} K")
    print(f"low-frequency cutoff = {args.cutoff:.1f} cm^-1 (Grimme quasi-RRHO)")
    print(f"ZPE             = {ZPE:.6f}  eV")
    print(f"U_vib(T)        = {U_vib:.6f}  eV  (excl. ZPE)")
    if args.gas:
        print(f"S_trans         = {S_trans_J*N_A:.3f}  J/(mol*K)")
        print(f"S_rot           = {S_rot_J*N_A:.3f}  J/(mol*K)")
    print(f"S_vib(qRRHO)    = {S_vib_J*N_A:.3f}  J/(mol*K)")
    print(f"T*S_total       = {TS_eV:.6f}  eV")
    print(f"H_thermal_corr  = {H_thermal:.6f}  eV  (ZPE + U_vib + pV/trans/rot)")
    print(f"G_corr          = ZPE + H_thermal - T*S = {G_corr:.6f}  eV")
    print()
    print("# To get the absolute Gibbs free energy of this stationary point,")
    print("# add G_corr to the SCF electronic energy in the CP2K geo_opt output:")
    print("#     G_total = E_elec + G_corr")
    return 0


if __name__ == "__main__":
    sys.exit(main())
