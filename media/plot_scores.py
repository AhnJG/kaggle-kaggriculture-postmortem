"""Score trajectory chart for README. Data: experiments/EXPERIMENT_LOG.md §2.1 (team score = best active slot)."""
import datetime as dt, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt, matplotlib.dates as md
D=lambda s: dt.datetime.strptime(s, "%m-%d %H:%M").replace(year=2026)
team=[("09-07 06:20",314.8),("09-09 07:30",330.6),("09-10 23:16",2188.4),("09-15 12:00",1862.6),("09-16 12:00",1726.6),
      ("09-18 12:00",1638.5),("09-19 15:20",2421.6),("09-20 12:00",2410.4),("09-23 12:00",2425.7),("09-28 05:27",2381.4),
      ("09-28 23:38",2198.8),("09-29 11:45",2127.1),("09-29 23:33",1861.6),("09-30 20:47",1622.2)]
bronze=[("09-16 12:00",2442.5),("09-18 12:00",2395.3),("09-19 15:20",2418.9),("09-20 12:00",2444.5),("09-23 12:00",2346.1),
        ("09-24 12:00",2302.8),("09-28 05:27",2096.5),("09-28 23:38",2042.8),("09-29 11:45",1983.1),("09-29 23:33",1916.2),("09-30 20:47",1852.0)]
notes=[("09-10 23:16",2188.4,"Switch to tape replay\n(public #9 exact) 2188",(-10,-62)),
       ("09-23 12:00",2425.7,"EXP-016 best 2426",(-40,14)),
       ("09-30 20:47",1622.2,"Final slots\nresubmitted 1622",(-92,-6))]
T={"light":dict(bg="#fcfcfb",ink="#0b0b0b",ink2="#52514e",mut="#898781",grid="#e1e0d9",base="#c3c2b7",s1="#2a78d6"),
   "dark":dict(bg="#1a1a19",ink="#f0efec",ink2="#c3c2b7",mut="#898781",grid="#2c2c2a",base="#383835",s1="#3987e5")}
for mode,c in T.items():
    plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10})
    fig,ax=plt.subplots(figsize=(9,4.2),dpi=160); fig.patch.set_facecolor(c["bg"]); ax.set_facecolor(c["bg"])
    bx=[D(a) for a,_ in bronze]; by=[b for _,b in bronze]
    ax.plot(bx,by,color=c["mut"],lw=1.5,ls=(0,(4,3)),label="Bronze line (top 10%)",zorder=2)
    tx=[D(a) for a,_ in team]; ty=[b for _,b in team]
    ax.plot(tx,ty,color=c["s1"],lw=2,marker="o",ms=4.5,mec=c["bg"],mew=1.2,label="Team Sian (best active slot)",zorder=3)
    for a,y,txt,off in notes:
        ax.annotate(txt,(D(a),y),xytext=off,textcoords="offset points",color=c["ink2"],fontsize=8.5,
                    arrowprops=dict(arrowstyle="-",color=c["mut"],lw=0.8))
    ax.set_ylim(0,2800); ax.set_xlim(D("09-06 00:00"),D("10-01 12:00"))
    ax.xaxis.set_major_locator(md.DayLocator(interval=4)); ax.xaxis.set_major_formatter(md.DateFormatter("%b %d"))
    ax.grid(axis="y",color=c["grid"],lw=0.8); ax.set_axisbelow(True)
    for s in ("top","right","left"): ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(c["base"]); ax.tick_params(colors=c["mut"],length=0)
    ax.set_ylabel("Hosted rating",color=c["ink2"])
    ax.set_title("Kaggriculture public leaderboard score, Sep 2026",loc="left",color=c["ink"],fontsize=12,pad=12)
    leg=ax.legend(loc="lower right",frameon=False,fontsize=9); [t.set_color(c["ink2"]) for t in leg.get_texts()]
    fig.tight_layout(); fig.savefig(f"media/score_trajectory_{mode}.png",facecolor=c["bg"]); plt.close(fig)
print("ok")
