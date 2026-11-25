import random
from dataclasses import dataclass


@dataclass
class Job:
    pid: str
    at: int
    bt: int
    pr: int


def run_sim(jobs, aging=0, fcfs_mode=False):
    jobs = sorted(jobs, key=lambda j: (j.at, j.pid))
    done, chart, t = {}, [], 0
    while len(done) < len(jobs):
        ready = [j for j in jobs if j.at <= t and j.pid not in done]
        if not ready:
            t = min(j.at for j in jobs if j.pid not in done)
            continue
        if fcfs_mode:
            cur = min(ready, key=lambda j: (j.at, j.pid))
        else:
            cur = min(
                ready,
                key=lambda j: (
                    max(1, j.pr - (max(0, t - j.at) // aging)) if aging > 0 else j.pr,
                    j.at,
                    j.pid,
                ),
            )
        wt = t - cur.at
        ct = t + cur.bt
        tat = ct - cur.at
        chart.append((cur.pid, t, ct))
        done[cur.pid] = {"AT": cur.at, "BT": cur.bt, "PR": cur.pr, "CT": ct, "TAT": tat, "WT": wt, "RT": wt}
        t = ct
    return chart, done


def avg_stats(stats):
    vals = list(stats.values())
    n = len(vals)
    return {k: sum(v[k] for v in vals) / n for k in ("TAT", "WT", "RT")}


def show_table(jobs, stats):
    print(f"{'PID':<5} {'AT':>3} {'BT':>3} {'PR':>3} {'CT':>3} {'TAT':>4} {'WT':>3} {'RT':>3}")
    for j in jobs:
        s = stats[j.pid]
        print(f"{j.pid:<5} {s['AT']:>3} {s['BT']:>3} {s['PR']:>3} {s['CT']:>3} {s['TAT']:>4} {s['WT']:>3} {s['RT']:>3}")
    a = avg_stats(stats)
    print(f"Average TAT = {a['TAT']:.2f}   Average WT = {a['WT']:.2f}   Average RT = {a['RT']:.2f}")


def show_gantt(chart):
    merged = []
    for pid, s, e in chart:
        if merged and merged[-1][0] == pid and merged[-1][2] == s:
            merged[-1] = (pid, merged[-1][1], e)
        else:
            merged.append((pid, s, e))
    print("Gantt : " + "".join(f"| {pid} " for pid, _, _ in merged) + "|")
    print("Time  : " + "   ".join([str(merged[0][1])] + [str(e) for _, _, e in merged]))


def demo_1(aging=4):
    print("DEMO 1 : Starvation of a low-priority process (non-preemptive)")
    jobs = [Job(f"H{i}", 3 * (i - 1) + 1, 3, 1) for i in range(1, 7)]
    jobs.insert(1, Job("L", 2, 5, 6))
    for label, step in [("Plain priority (no aging)", 0), (f"Hybrid with aging (every {aging} units)", aging)]:
        chart, stats = run_sim(jobs, aging=step)
        print(f"\n--- {label} ---")
        show_table(jobs, stats)
        show_gantt(chart)
        print(f"Waiting time of L = {stats['L']['WT']}")


def demo_2(seed=19, n=12, aging=5):
    print(f"\nDEMO 2 : FCFS vs Hybrid multi-priority FCFS ({n} random processes, seed={seed})")
    rng = random.Random(seed)
    jobs = sorted([Job(f"P{i + 1}", rng.randint(0, 14), rng.randint(2, 9), rng.randint(1, 5)) for i in range(n)], key=lambda j: (j.at, j.pid))
    print(f"{'PID':<5} {'AT':>3} {'BT':>3} {'PR':>3}")
    for j in jobs:
        print(f"{j.pid:<5} {j.at:>3} {j.bt:>3} {j.pr:>3}")
    _, m_f = run_sim(jobs, fcfs_mode=True)
    _, m_h = run_sim(jobs, aging=aging)
    af, ah = avg_stats(m_f), avg_stats(m_h)
    print(f"\n{'Metric':<22} {'FCFS':>10} {'Hybrid':>10}")
    for k, label in [("RT", "Avg response time"), ("WT", "Avg waiting time"), ("TAT", "Avg turnaround time")]:
        print(f"{label:<22} {af[k]:>10.2f} {ah[k]:>10.2f}")
    print(f"{'Max waiting time':<22} {max(v['WT'] for v in m_f.values()):>10} {max(v['WT'] for v in m_h.values()):>10}")
    p1 = [j.pid for j in jobs if j.pr == 1]
    if p1:
        print(f"{'Avg RT (priority 1)':<22} {sum(m_f[x]['RT'] for x in p1)/len(p1):>10.2f} {sum(m_h[x]['RT'] for x in p1)/len(p1):>10.2f}")
    gain = ((af["RT"] - ah["RT"]) / af["RT"]) * 100 if af["RT"] else 0.0
    print(f"\nChange in average response time vs FCFS (positive = better): {gain:+.2f}%")


if __name__ == "__main__":
    demo_1()
    demo_2()