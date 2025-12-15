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

    # Source attribution
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(50, height - 70, "Sources: FanGraphs.com, Baseball-Reference.com, MLB.com Official Statistics")

    y_position = height - 110
    
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
                "Note: OPS has limitations as it assumes OBP and SLUG are equals, though OBP is actually",
                "about twice as valuable as SLUG. (Source: FanGraphs)",
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
                "Limitations: ERA can be influenced by factors outside a pitcher's control,",
                "particularly defense quality. (Source: FanGraphs)",
                "ERA is the traditional measure of pitcher effectiveness."
            ]
        },
        {
            "title": "FIP (Fielding Independent Pitching)",
            "content": [
                "Definition: Estimates a pitcher's ERA based only on events they control:",
                "strikeouts, walks, hit-by-pitches, and home runs. (Source: FanGraphs)",
                "Formula: FIP = ((13*HR + 3*(BB+HBP) - 2*K) / IP) + Constant",
                "Interpretation: FIP is scaled the same way as ERA.",
                " - If FIP < ERA: Pitcher has been unlucky or has poor defense",
                " - If FIP > ERA: Pitcher has been lucky or has excellent defense",
                "FIP removes defense altogether and is considered a better predictor of",
                "future performance than ERA. (Source: FanGraphs)"
            ]
        },
        {
            "title": "wRC+ (Weighted Runs Created Plus)",
            "content": [
                "Definition: Comprehensive offensive statistic measuring runs created,",
                "adjusted for park and league effects. (Source: FanGraphs)",
                "Formula: wRC+ = (((wRAA/PA + League R/PA) + (League R/PA – Park Factor",
                "* League R/PA)) / (AL or NL wRC/PA excluding pitchers)) * 100",
                "Scale: 100 is always league average.",
                "Interpretation:",
                " - 100: League Average",
                " - 80: 20% worse than average",
                " - 120: 20% better than average",
                " - 150: All-Star / MVP Candidate",
                "Context-neutral and allows comparison across eras. (Source: FanGraphs)"
            ]
        },
        {
            "title": "WAR (Wins Above Replacement)",
            "content": [
                "Definition: Measures a player's total value compared to a 'replacement level'",
                "player. A concept rather than one individual statistic. (Source: FanGraphs)",
                "Versions: fWAR (FanGraphs), rWAR (Baseball-Reference), WARP (Baseball Prospectus)",
                "Key Differences:",
                " - fWAR uses FIP for pitchers, UZR for fielding",
                " - rWAR uses runs allowed, DRS for fielding",
                "Interpretation (for a full season):",
                " - 0-2 WAR: Reserve / Bench player",
                " - 2-4 WAR: Solid Starter",
                " - 4-6 WAR: All-Star",
                " - 6+ WAR: MVP Candidate",
                "Note: Different WAR calculations provide complementary views. (Source: FanGraphs)"
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
