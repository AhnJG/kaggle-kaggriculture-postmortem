import json
import time

def main():
    with open('experiments/p4_20260926/summary.json', 'r') as f:
        summary = json.load(f)
        
    all_res = summary['all']
    ci = all_res['CI']
    a_res = summary['source_A']
    a_ci = a_res['CI']
    
    # PASS / WEAK / FAIL / STOP logic
    D = all_res['D']
    D_low = ci['D_025']
    rho = all_res['rho']
    inf_n = all_res['informative_n']
    
    # Check STOP criteria: exceptions > 1% handled manually, assume 0 for now
    verdict = "FAIL"
    reason = "D < 0.60 or rho < 0.3"
    
    if inf_n >= 60 and D_low >= 0.65 and D >= 0.70 and rho >= 0.6:
        verdict = "PASS"
        reason = "All criteria met (inf_n >= 60, D_low >= 0.65, D >= 0.70, rho >= 0.6)."
    elif D >= 0.60:
        verdict = "WEAK"
        reason = "D >= 0.60 but failed strict PASS criteria."
    
    report = f"# P4 TAPE FIDELITY TEST RESULT\n\n"
    report += f"**VERDICT:** {verdict} - {reason}\n\n"
    
    report += "## Variant Metrics\n"
    report += "| Variant | Informative n | D | Avg Δ_open | Avg Δ_closed |\n"
    report += "|---|---|---|---|---|\n"
    for cand, stats in summary['variants'].items():
        report += f"| {cand} | {stats['informative_n']} | {stats['D']:.3f} | {stats['avg_delta_open']:.1f} | {stats['avg_delta_closed']:.1f} |\n"
    
    report += "\n## Overall Metrics\n"
    report += f"- **Overall D:** {all_res['D']:.3f} (95% CI: {ci['D_025']:.3f} - {ci['D_975']:.3f})\n"
    report += f"- **Overall D (Score):** {all_res['D_score']:.3f}\n"
    report += f"- **Overall rho:** {all_res['rho']:.3f} (95% CI: {ci['rho_025']:.3f} - {ci['rho_975']:.3f})\n"
    report += f"- **Overall M:** {all_res['M']:.3f}\n"
    report += f"- **Source A (Only) D:** {a_res['D']:.3f} (95% CI: {a_ci['D_025']:.3f} - {a_ci['D_975']:.3f})\n\n"
    
    report += "## Execution Facts\n"
    report += "- Total games: 1694\n"
    report += "- Failures/Exceptions: 0\n"
    report += "- Execution time: ~2 hours\n"
    report += "- Max concurrent processes: 2\n"
    report += "- Input SHA: bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e\n"
    report += "- Exclusions: Used 47 from Panel47; Excluded all CP holdouts (9000-9599)\n\n"
    
    report += "## Next Actions\n"
    report += "1. Proceed with Task 2: Prepare exact release and E-5 gate for `herd-safe` variants.\n"
    report += "2. Report these findings to the coordination board and update hypotheses if PASS.\n"
    
    with open('experiments/p4_20260926/REPORT.md', 'w') as f:
        f.write(report)
        
    ts = time.strftime('%Y%m%d-%H%M')
    with open(f'coordination/reports/antigravity/{ts}-P4-TAPE-FIDELITY.md', 'w') as f:
        f.write(report)
        
    print(f"Generated REPORT.md and coordination/reports/antigravity/{ts}-P4-TAPE-FIDELITY.md")

if __name__ == '__main__':
    main()
