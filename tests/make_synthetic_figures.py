from pathlib import Path
import matplotlib.pyplot as plt

OUT=Path(__file__).resolve().parent/"fixtures"
OUT.mkdir(exist_ok=True)

# Genuinely clean example: generous label padding.
fig,ax=plt.subplots(figsize=(6,3))
ax.scatter([1,2,3],[1,2,1.5])
ax.set_xlabel("X", labelpad=14)
ax.set_ylabel("Y", labelpad=10)
ax.text(2.8,2.25,"clean annotation",ha="right")
fig.subplots_adjust(left=.16,right=.96,top=.92,bottom=.28)
fig.savefig(OUT/"clean.pdf")
plt.close(fig)

# Deliberate text overlap.
fig,ax=plt.subplots(figsize=(6,3))
ax.scatter([1,2,3],[1,2,1.5])
ax.text(2.0,1.8,"OVERLAP TEXT A",fontsize=10)
ax.text(2.0,1.8,"OVERLAP TEXT B",fontsize=10)
fig.subplots_adjust(left=.16,right=.96,top=.92,bottom=.25)
fig.savefig(OUT/"text_overlap.pdf")
plt.close(fig)

# Card example for layout-contract audit.
fig=plt.figure(figsize=(6,3))
ax=fig.add_axes([0,0,1,1])
ax.axis("off")
from matplotlib.patches import Rectangle
ax.add_patch(Rectangle((.10,.25),.35,.45,fill=False,linewidth=1.0))
ax.text(.14,.48,"CARD TEXT",fontsize=10,va="center")
fig.savefig(OUT/"card_clean.pdf")
plt.close(fig)
