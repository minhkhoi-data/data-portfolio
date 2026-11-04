"""Read-only static Python preview of delivered CSVs, not a Desktop screenshot."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import pandas as pd
from pipeline import ROOT

def main():
    out=ROOT/'outputs/figures';out.mkdir(exist_ok=True)
    k=pd.read_csv(ROOT/'outputs/kpi_summary.csv').set_index('metric').value
    f=pd.read_csv(ROOT/'outputs/ordered_funnel.csv');d=pd.read_csv(ROOT/'outputs/device_performance.csv')
    c=pd.read_csv(ROOT/'outputs/channel_performance.csv');m=pd.read_csv(ROOT/'outputs/monthly_performance.csv')
    navy='#163A70';teal='#238B8D';fig,axes=plt.subplots(2,2,figsize=(16,10),facecolor='#F7FAFD')
    fig.suptitle('GOOGLE MERCHANDISE STORE | GA4 PUBLIC SAMPLE',fontsize=18,color=navy,y=.98,fontweight='bold')
    fig.text(.5,.931,f"Sessions {k['Sessions']:,.0f}    Users {k['Users']:,.0f}    Purchase events {k['Purchase Events']:,.0f}    Revenue USD {k['Revenue']:,.0f}    Session CVR {k['Session Conversion Rate']:.2%}",ha='center',fontsize=12,color=navy)
    ax=axes[0,0];bars=ax.barh(f.stage,f.sessions,color=navy);ax.invert_yaxis()
    ax.bar_label(bars,labels=[f'{v:,}' for v in f.sessions],padding=4,fontsize=10)
    ax.set_xlim(0,f.sessions.max()*1.24);ax.set_xlabel('Sessions reaching each step in strict timestamp order')
    ax.set_title('Ordered journey: no inferred intermediate steps',loc='left',fontsize=13,pad=15)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x,p:f'{x/1000:.0f}k'))
    ax=axes[0,1];d=d.sort_values('device_category');bars=ax.bar(d.device_category,d.conversion_rate*100,color=teal)
    ax.bar_label(bars,labels=[f'{v:.2%}' for v in d.conversion_rate],padding=5,fontsize=11)
    ax.set_ylim(0,max(d.conversion_rate)*100*1.35);ax.set_ylabel('Session purchase conversion (%)')
    ax.set_title('Device conversion: descriptive association',loc='left',fontsize=13,pad=15)
    ax=axes[1,0];c=c.sort_values('revenue_per_session');bars=ax.barh(c.channel,c.revenue_per_session,color=navy)
    ax.bar_label(bars,labels=[f'${v:.2f}' for v in c.revenue_per_session],padding=4,fontsize=10)
    ax.set_xlim(0,c.revenue_per_session.max()*1.25);ax.set_xlabel('USD attributed purchase-event revenue / observed session')
    ax.set_title('First-user channel: unknown / masked retained',loc='left',fontsize=13,pad=15)
    ax=axes[1,1];bars=ax.bar(m.year_month,m.revenue/1000,color=teal)
    ax.bar_label(bars,labels=[f'${v/1000:,.1f}k' for v in m.revenue],padding=5,fontsize=11)
    ax.set_ylim(0,m.revenue.max()/1000*1.3);ax.set_ylabel('Purchase-event revenue (USD thousands)')
    ax.set_title('Revenue by purchase event month',loc='left',fontsize=13,pad=15)
    for ax in axes.ravel():
        ax.set_facecolor('#F7FAFD');ax.spines[['top','right']].set_visible(False);ax.grid(axis='x',alpha=.12);ax.set_axisbelow(True)
    fig.text(.5,.045,'2020-11-01 to 2021-01-31 | Obfuscated public data | Purchase events are not verified orders | Product details and A/B assignments absent',ha='center',fontsize=10,color=navy)
    fig.text(.5,.02,'Static Python preview from delivered tables. Power BI Desktop rendering has not been verified.',ha='center',fontsize=10,color='#596C80')
    fig.tight_layout(rect=(0,.08,1,.9));fig.savefig(out/'ga4_overview.png',dpi=150);plt.close(fig)
    print('PASS: static GA4 preview saved; not a native screenshot')

if __name__=='__main__':main()
