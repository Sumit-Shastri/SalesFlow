"""SalesFlow PDF generator. Requires: pip install reportlab

Usage:
    from report_pdf_generator import generate_sales_report
    generate_sales_report(parsed_data, ai_insights, 'sales_report.pdf')

Charts may be BytesIO, bytes, filesystem paths, PIL images, or ReportLab ImageReader.
No analytics are invented: unavailable inputs appear as unavailable, not fake values.
"""
from __future__ import annotations

from datetime import datetime
from html import escape
from io import BytesIO
from pathlib import Path
import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, Flowable,
)

NAVY = colors.HexColor('#14243B')
BLUE = colors.HexColor('#2867D8')
PALE = colors.HexColor('#EDF3FF')
INK = colors.HexColor('#243247')
MUTED = colors.HexColor('#66758A')
BORDER = colors.HexColor('#E0E6EF')
LIGHT = colors.HexColor('#F5F7FB')
GREEN = colors.HexColor('#087F6F')
ORANGE = colors.HexColor('#A86410')
WHITE = colors.white
W, H = A4
MARGIN = 43
CW = W - 2 * MARGIN


def _fonts():
    candidates = [
        ('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),
        ('C:/Windows/Fonts/arial.ttf', 'C:/Windows/Fonts/arialbd.ttf'),
    ]
    for normal, bold in candidates:
        if os.path.isfile(normal) and os.path.isfile(bold):
            pdfmetrics.registerFont(TTFont('SFRegular', normal))
            pdfmetrics.registerFont(TTFont('SFBold', bold))
            pdfmetrics.registerFontFamily('SFRegular', normal='SFRegular', bold='SFBold')
            return 'SFRegular', 'SFBold'
    return 'Helvetica', 'Helvetica-Bold'

FONT, BOLD = _fonts()
ST = {
    'title': ParagraphStyle('title', fontName=BOLD, fontSize=24, leading=31, textColor=NAVY, spaceAfter=9),
    'section': ParagraphStyle('section', fontName=BOLD, fontSize=19, leading=25, textColor=NAVY, spaceAfter=9),
    'sub': ParagraphStyle('sub', fontName=BOLD, fontSize=11.3, leading=16, textColor=NAVY, spaceBefore=13, spaceAfter=8),
    'body': ParagraphStyle('body', fontName=FONT, fontSize=8.5, leading=13.8, textColor=INK, spaceAfter=7),
    'small': ParagraphStyle('small', fontName=FONT, fontSize=7.5, leading=11.5, textColor=MUTED, spaceAfter=6),
    'label': ParagraphStyle('label', fontName=BOLD, fontSize=7, leading=11, textColor=MUTED),
    'value': ParagraphStyle('value', fontName=BOLD, fontSize=12.5, leading=18, textColor=NAVY),
    'tablehead': ParagraphStyle('tablehead', fontName=BOLD, fontSize=7, leading=10, textColor=WHITE),
    'table': ParagraphStyle('table', fontName=FONT, fontSize=7, leading=10.5, textColor=INK),
    'cardtitle': ParagraphStyle('cardtitle', fontName=BOLD, fontSize=9, leading=13, textColor=NAVY, spaceAfter=4),
}


def p(text, style='body'):
    return Paragraph(escape(str(text if text is not None else 'Not available')).replace('\n', '<br/>'), ST[style])


def money(value):
    if value is None: return 'Not available'
    try: return f'₹{float(value):,.2f}'
    except (TypeError, ValueError): return str(value)


def num(value):
    if value is None: return 'Not available'
    try: return f'{int(value):,}'
    except (TypeError, ValueError): return str(value)


def pct(value):
    if value is None: return 'Not available'
    if isinstance(value, str): return value
    try: return f'{float(value):+.1f}%'
    except (TypeError, ValueError): return str(value)


def period(month):
    try: return datetime.strptime(str(month), '%Y-%m').strftime('%b %Y')
    except ValueError: return str(month)


def box(contents, width=CW, bg=LIGHT, pad=13, border=BORDER):
    if not isinstance(contents, list): contents = [contents]
    table = Table([[contents]], colWidths=[width])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0),(-1,-1),bg), ('BOX',(0,0),(-1,-1),.65,border),
        ('LEFTPADDING',(0,0),(-1,-1),pad),('RIGHTPADDING',(0,0),(-1,-1),pad),
        ('TOPPADDING',(0,0),(-1,-1),pad),('BOTTOMPADDING',(0,0),(-1,-1),pad),
    ]))
    return table


def metrics(items):
    width = CW / len(items)
    row = []
    for label, value, caption in items:
        row.append([p(label.upper(),'label'),Spacer(1,5),p(value,'value'),Spacer(1,3),p(caption,'small')])
    t = Table([row], colWidths=[width]*len(row))
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),PALE),('BOX',(0,0),(-1,-1),.7,BORDER),
        ('INNERGRID',(0,0),(-1,-1),.4,BORDER),('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),7),
        ('TOPPADDING',(0,0),(-1,-1),11),('BOTTOMPADDING',(0,0),(-1,-1),9),
    ]))
    return t


def data_table(headers, rows, widths=None):
    if not rows: return box(p('No tabular data provided.','small'))
    values = [[p(h,'tablehead') for h in headers]] + [[p(x,'table') for x in row] for row in rows]
    t = Table(values, colWidths=widths, repeatRows=1, hAlign='LEFT')
    cmds = [
        ('BACKGROUND',(0,0),(-1,0),NAVY),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('LINEBELOW',(0,1),(-1,-1),.4,BORDER),
        ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),7),
        ('TOPPADDING',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),9),
    ]
    for i in range(2,len(values),2): cmds.append(('BACKGROUND',(0,i),(-1,i),LIGHT))
    t.setStyle(TableStyle(cmds))
    return t


class Chart(Flowable):
    """Draw image to fixed height, preserving its original aspect ratio."""
    def __init__(self, source, width=CW, height=190):
        super().__init__()
        self.width, self.height = width, height
        self.reader = None
        if source is None or isinstance(source,str) and source.startswith('<'):
            return
        try:
            if isinstance(source, BytesIO):
                source.seek(0)
                self.reader = ImageReader(BytesIO(source.getvalue()))
            elif isinstance(source, bytes): self.reader = ImageReader(BytesIO(source))
            else: self.reader = ImageReader(source)
        except Exception:
            self.reader = None

    def draw(self):
        if self.reader is None:
            self.canv.setFillColor(LIGHT)
            self.canv.roundRect(0,0,self.width,self.height,8,stroke=0,fill=1)
            self.canv.setFont(FONT,8)
            self.canv.setFillColor(MUTED)
            self.canv.drawCentredString(self.width/2,self.height/2,'Chart not provided')
            return
        iw, ih = self.reader.getSize()
        scale = min(self.width / iw, self.height / ih)
        dw, dh = iw*scale, ih*scale
        self.canv.drawImage(self.reader,(self.width-dw)/2,(self.height-dh)/2,dw,dh,mask='auto')


def chart_pair(left, right, height=184):
    col = (CW-14)/2
    t = Table([[Chart(left,col,height),Chart(right,col,height)]], colWidths=[col+7,col+7])
    t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),7)]))
    return t


def section(story, n, title, description):
    story.extend([p(f'SECTION {n:02d}','label'),Spacer(1,11),p(title,'section'),p(description,'small'),Spacer(1,15)])


def explanation(story, insights, key):
    value = insights.get('section_explanations',{}).get(key)
    if value:
        story.extend([p('Analysis & Interpretation','sub'),box(p(value))])


def entry(story, title, body, extra=None):
    children = [p(title,'cardtitle'),p(body)]
    if extra: children.append(p(extra,'small'))
    story.extend([box(children),Spacer(1,9)])


def _page(canvas, doc):
    canvas.saveState()
    page = doc.page
    canvas.setStrokeColor(BORDER)
    canvas.line(MARGIN,H-47,W-MARGIN,H-47)
    canvas.line(MARGIN,46,W-MARGIN,46)
    canvas.setFont(BOLD,10)
    canvas.setFillColor(NAVY)
    canvas.drawString(MARGIN,H-35,'▮ SALESFLOW')
    canvas.setFont(FONT,7)
    canvas.setFillColor(MUTED)
    canvas.drawRightString(W-MARGIN,H-34,'SALES PERFORMANCE REPORT')
    canvas.drawString(MARGIN,32,'SALESFLOW / GENERATED REPORT')
    canvas.drawRightString(W-MARGIN,32,f'{page:02d}')
    canvas.restoreState()


def generate_sales_report(parsed_data: dict, ai_insights: dict, output_path: str | Path) -> str:
    """Generate a report using parser output and AI insight generator output."""
    if not isinstance(parsed_data,dict) or not isinstance(ai_insights,dict):
        raise TypeError('parsed_data and ai_insights must be dictionaries')
    output_path = str(output_path)
    Path(output_path).parent.mkdir(parents=True,exist_ok=True)
    doc = BaseDocTemplate(output_path,pagesize=A4,leftMargin=MARGIN,rightMargin=MARGIN,
                          topMargin=69,bottomMargin=65,title='SalesFlow Sales Performance Report',author='SalesFlow')
    frame = Frame(MARGIN,65,CW,H-134,leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)
    doc.addPageTemplates(PageTemplate(id='main',frames=[frame],onPage=_page))
    s=[]
    cover=parsed_data.get('report_cover',{})
    summary=parsed_data.get('executive_summary',{})
    overall=parsed_data.get('overall_sales_performance',{})
    prod=parsed_data.get('product_performance_analysis',{})
    monthly=parsed_data.get('monthly_performance_analysis',{})
    growth=parsed_data.get('growth_analysis',{})
    ins=ai_insights

    # 1. Cover
    s.extend([Spacer(1,35),p('SALESFLOW  /  SALES ANALYTICS','label'),Spacer(1,19),
              p(cover.get('report_type','Sales Performance Report'),'title'),
              p(cover.get('report_title','Sales analysis'),'sub'),
              p(cover.get('company_name','Company not specified'),'body'),Spacer(1,24)])
    cover_fields=[
        ('REPORTING PERIOD',cover.get('reporting_period','Not specified')),
        ('GENERATED ON',cover.get('generated_on','Not specified')),
        ('REPORT TYPE',cover.get('report_type','Sales Performance Report')),
        ('COMPANY NAME',cover.get('company_name','Not specified')),
        ('DATA SOURCE',cover.get('data_source','Not specified')),
        ('PREPARED USING',cover.get('prepared_using','SalesFlow')),
        ('REPORT TITLE',cover.get('report_title','Sales analysis')),
        ('RECORDS ANALYZED',num(cover.get('number_of_sales_record'))),
    ]
    cover_rows=[]
    for i in range(0,len(cover_fields),2):
        cover_rows.append([[p(cover_fields[j][0],'label'),Spacer(1,4),p(cover_fields[j][1],'body')]
                           for j in (i,i+1)])
    ct=Table(cover_rows,colWidths=[CW/2,CW/2])
    ct.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),LIGHT),('INNERGRID',(0,0),(-1,-1),5,WHITE),
                            ('BOX',(0,0),(-1,-1),.6,BORDER),('VALIGN',(0,0),(-1,-1),'TOP'),
                            ('LEFTPADDING',(0,0),(-1,-1),13),('TOPPADDING',(0,0),(-1,-1),11),
                            ('BOTTOMPADDING',(0,0),(-1,-1),8)]))
    s.extend([ct,Spacer(1,20),p('DATA QUALITY NOTES','sub')])
    notes=cover.get('data_quality_notes') or ['No data-quality notes provided.']
    s.append(box([p('• '+str(x)) for x in notes],bg=colors.HexColor('#FFF6E9')))
    s.append(PageBreak())

    # 2. Executive summary
    section(s,2,'Executive Summary','Key metrics and evidence-based business interpretation.')
    s.append(metrics([('Total revenue',money(summary.get('total_revenue')),'Period total'),
                      ('Units sold',num(summary.get('total_units_sold')),'Period total'),
                      ('Products',num(summary.get('number_of_products')),'Distinct products'),
                      ('Revenue growth',pct(summary.get('overall_revenue_growth')),'Reported growth')]))
    explanation(s,ins,'executive_summary')
    findings=ins.get('key_findings',[])
    if findings:
        s.append(p('Key Business Insights','sub'))
        for f in findings[:2]: entry(s,f.get('title','Finding'),f.get('finding',''),f.get('evidence'))
    s.append(PageBreak())

    # 3. Overall performance
    section(s,3,'Overall Sales Performance','Period KPIs, monthly breakdown and revenue extremes.')
    s.append(metrics([('Revenue',money(overall.get('total_revenue')),'Period total'),
                      ('Units',num(overall.get('total_units_sold')),'Sold'),
                      ('Products',num(overall.get('number_of_products')),'Distinct'),
                      ('Records',num(overall.get('number_of_sales_records')),'Transactions'),
                      ('Avg. price',money(overall.get('average_selling_price')),'Parser value')]))
    s.append(p('Monthly Revenue Summary','sub'))
    months=overall.get('monthly_revenue_summary',{})
    rows=[]
    for key in sorted(months):
        d=months[key]
        rows.append([period(key),money(d.get('total_revenue')),num(d.get('total_quantity')),
                     num(d.get('sales_records')),money(d.get('average_selling_price'))])
    s.append(data_table(['Month','Revenue','Units','Records','Avg. price'],rows,[95,116,80,79,CW-370]))
    high=overall.get('highest_revenue_month',{})
    low=overall.get('lowest_revenue_month',{})
    s.append(p('Period Snapshot','sub'))
    s.append(metrics([('Highest revenue',str(high.get('month_in_word','N/A'))+' '+str(high.get('month',''))[:4],money(high.get('total_revenue'))),
                      ('Lowest revenue',str(low.get('month_in_word','N/A'))+' '+str(low.get('month',''))[:4],money(low.get('total_revenue')))]))
    explanation(s,ins,'overall_sales_performance')
    s.append(PageBreak())

    # 4. Product
    section(s,4,'Product Performance Analysis','Product revenue, performance and the implications for the product mix.')
    s.append(p('Revenue by Product','sub'))
    s.append(Chart(prod.get('revenue_chart'),CW,210))
    s.append(p('Product Performance','sub'))
    s.append(Chart(prod.get('performance_chart'),CW,210))
    explanation(s,ins,'product_performance_analysis')
    s.append(PageBreak())

    # 5. Time
    section(s,5,'Time and Trend Analysis','Observed monthly revenue and unit movement; partial months should be interpreted carefully.')
    s.append(p('Monthly Revenue and Units','sub'))
    s.append(chart_pair(monthly.get('monthly_revenue_chart'),monthly.get('monthly_units_chart'),190))
    s.append(p('Month-over-Month Movement','sub'))
    s.append(Chart(monthly.get('month-over-month-table'),CW,140))
    hi=monthly.get('highest_revenue_day',{})
    lo=monthly.get('lowest_revenue_day',{})
    s.append(metrics([('Highest day',str(hi.get('day','N/A')),money(hi.get('total_revenue'))),
                      ('Lowest day',str(lo.get('day','N/A')),money(lo.get('total_revenue')))]))
    explanation(s,ins,'monthly_performance_analysis')
    s.append(PageBreak())

    # 6. Growth
    section(s,6,'Growth Analysis','Latest month-over-month change and product growth patterns.')
    mom=growth.get('latest_MoM_revenue_growth',{})
    q=growth.get('quantity_growth',{})
    s.append(metrics([('Latest MoM',mom.get('latest_MoM_growth_revenue','N/A'),
                       f"{mom.get('next_month','')} vs {mom.get('prev_month','')}"),
                      ('Revenue change',money(growth.get('revenue_change')),'Absolute difference'),
                      ('Quantity growth',pct(q.get('percentage')),f"{num(q.get('unit_change'))} units"),
                      ('Avg. MoM growth',pct(growth.get('avg_monthly_revenue_growth')),'Valid intervals')]))
    s.append(p('Product Revenue Growth','sub'))
    s.append(Chart(growth.get('product_revenue_growth_table'),CW,235))
    s.append(metrics([('Highest product',growth.get('highest_revenue_growth_product','N/A'),pct(growth.get('highest_revenue_growth_rate'))),
                      ('Lowest product',growth.get('lowest_revenue_growth_product','N/A'),pct(growth.get('lowest_revenue_growth_rate')))]))
    explanation(s,ins,'growth_analysis')
    s.append(PageBreak())

    # 7. Findings and recommendations
    section(s,7,'Key Findings and Recommendations','Measured observations followed by suggested investigations.')
    s.append(p('A. Key Findings','sub'))
    for i,f in enumerate(ins.get('key_findings',[]),1):
        entry(s,f'{i}. {f.get("title","Finding")}',f.get('finding',''),
              'Evidence: '+str(f.get('evidence',''))+'\nBusiness significance: '+str(f.get('business_significance','')))
    s.append(p('B. Recommendations','sub'))
    for i,r in enumerate(ins.get('recommendations',[]),1):
        entry(s,f'{i}. {r.get("title","Recommendation")}',r.get('recommendation',''),
              'Reason: '+str(r.get('reason','')))
    s.append(PageBreak())

    # 8. Conclusion
    section(s,8,'Conclusion','Final interpretation and areas for follow-up.')
    s.append(p('Report Takeaway','sub'))
    s.append(box(p(ins.get('conclusion','No conclusion provided.')),bg=PALE))
    s.append(p('Areas Worth Investigating','sub'))
    for i,a in enumerate(ins.get('areas_worth_investigating',[]),1):
        entry(s,f'{i:02d}. {a.get("area","Investigation")}',a.get('reason',''),
              'Suggested analysis: '+str(a.get('suggested_analysis','')))
    s.append(Spacer(1,8))
    s.append(p('END OF REPORT  •  SALESFLOW','label'))
    doc.build(s)
    return output_path


if __name__ == '__main__':
    print('Import generate_sales_report(parsed_data, ai_insights, output_path) from this module.')
