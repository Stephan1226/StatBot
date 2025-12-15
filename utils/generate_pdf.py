from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

def create_pdf(filename):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 24)
    c.drawString(50, height - 50, "Baseball Sabermetrics Guide")
    
    y_position = height - 100
    
    metrics = [
        {
            "title": "OPS (On-base Plus Slugging)",
            "content": [
                "Definition: The sum of a player's On-Base Percentage (OBP) and Slugging Percentage (SLG).",
                "Formula: OPS = OBP + SLG",
                "Interpretation:",
                " - Below .700: Below Average",
                " - .700 - .800: Average",
                " - .800 - .900: Above Average",
                " - .900+: All-Star Level",
                " - 1.000+: MVP Level",
                "OPS is a quick and easy way to measure a hitter's overall offensive production."
            ]
        },
        {
            "title": "ERA (Earned Run Average)",
            "content": [
                "Definition: The average number of earned runs a pitcher gives up for every 9 innings pitched.",
                "Formula: ERA = (Earned Runs / Innings Pitched) * 9",
                "Interpretation:",
                " - Under 3.00: Excellent",
                " - 3.00 - 4.00: Good to Average",
                " - 4.00 - 5.00: Below Average",
                " - Over 5.00: Poor",
                "ERA is the standard measure of a pitcher's effectiveness, though it can be influenced by defense."
            ]
        },
        {
            "title": "FIP (Fielding Independent Pitching)",
            "content": [
                "Definition: A metric that estimates a pitcher's ERA based only on events they control: strikeouts, walks, hit-by-pitches, and home runs.",
                "Formula: FIP = ((13*HR + 3*(BB+HBP) - 2*K) / IP) + Constant",
                "Interpretation: FIP is on the same scale as ERA.",
                " - If FIP < ERA: The pitcher has been unlucky or has bad defense behind them.",
                " - If FIP > ERA: The pitcher has been lucky or has great defense helping them.",
                "FIP is often considered a better predictor of future performance than ERA."
            ]
        },
        {
            "title": "wRC+ (Weighted Runs Created Plus)",
            "content": [
                "Definition: A comprehensive offensive statistic that measures runs created, adjusted for league and park effects.",
                "Scale: 100 is always league average.",
                "Interpretation:",
                " - 100: League Average",
                " - 80: 20% worse than average",
                " - 120: 20% better than average",
                " - 150: All-Star / MVP Candidate",
                "wRC+ is widely regarded as the single best statistic for measuring a hitter's pure offensive value."
            ]
        },
        {
            "title": "WAR (Wins Above Replacement)",
            "content": [
                "Definition: A summary statistic that attempts to calculate a player's total value to their team in terms of wins compared to a 'replacement level' player.",
                "Interpretation (for a full season):",
                " - 0-2 WAR: Reserve / Bench player",
                " - 2-4 WAR: Solid Starter",
                " - 4-6 WAR: All-Star",
                " - 6+ WAR: MVP Candidate",
                "WAR accounts for batting, fielding, and baserunning (for position players) or pitching (for pitchers)."
            ]
        }
    ]
    
    for metric in metrics:
        if y_position < 200:
            c.showPage()
            y_position = height - 50
            
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, y_position, metric["title"])
        y_position -= 25
        
        c.setFont("Helvetica", 12)
        for line in metric["content"]:
            c.drawString(70, y_position, line)
            y_position -= 20
        
        y_position -= 20
        
    c.save()

if __name__ == "__main__":
    create_pdf("data/sabermetrics.pdf")
    print("PDF generated at data/sabermetrics.pdf")
