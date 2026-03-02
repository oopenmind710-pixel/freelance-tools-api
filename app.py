from flask import Flask, request, jsonify
from datetime import datetime
import os, math, re

app = Flask(__name__)

def get_data():
    if request.method == 'POST' and request.is_json:
        return request.get_json()
    return request.args.to_dict()

@app.route('/')
def home():
    return jsonify({
        "name": "OpenMind Freelance Tools API",
        "version": "2.0.0",
        "endpoints": 12,
        "categories": ["freelance", "ai-audit", "content", "business"],
        "docs": "https://oopenmind710-pixel.github.io/openmind-store/api-docs.html",
        "rapidapi": "coming soon",
        "free_tier": "100 calls/day",
        "pro": "$9.99/month unlimited"
    })

@app.route('/rate-calculator', methods=['GET','POST'])
def rate_calculator():
    d = get_data()
    annual = float(d.get('annual_target', 60000))
    vacation = int(d.get('weeks_vacation', 5))
    hours = float(d.get('hours_per_day', 7))
    overhead = float(d.get('overhead_percent', 30))
    expertise = d.get('expertise', 'mid')
    currency = d.get('currency', 'EUR')
    working_days = (52 - vacation) * 5
    with_overhead = annual * (1 + overhead / 100)
    mult = {'junior':0.7,'mid':1.0,'senior':1.3,'expert':1.7,'niche':2.0}.get(expertise, 1.0)
    tjm = round((with_overhead / working_days) * mult)
    fx = {'EUR':1.0,'USD':1.08,'GBP':0.85,'CHF':0.96}.get(currency, 1.0)
    return jsonify({
        "currency": currency,
        "annual_target": annual,
        "recommended_tjm": round(tjm * fx),
        "recommended_hourly": round(tjm / hours * fx),
        "recommended_monthly": round(tjm * 20 * fx),
        "working_days_year": working_days,
        "expertise": expertise,
        "note": "Add 20-40% for urgent/niche projects"
    })

@app.route('/ai-audit-score', methods=['GET','POST'])
def ai_audit_score():
    d = get_data()
    def b(k): return d.get(k,'').lower() in ['true','1','yes']
    criteria = {
        'automation_exists': b('has_automation'),
        'ai_tools_used': b('uses_ai_tools'),
        'data_structured': b('data_structured'),
        'team_trained': b('team_trained'),
        'ai_strategy': b('has_ai_strategy'),
        'budget_allocated': b('budget_allocated'),
        'processes_documented': b('processes_documented'),
        'kpis_measured': b('kpis_measured'),
    }
    score = round(sum(criteria.values()) / len(criteria) * 100)
    levels = [(25,"Débutant","Start by automating 1 repetitive process",(0,3000)),
              (50,"Explorateur","Train team on AI basics, pilot 2-3 tools",(3000,8000)),
              (75,"Intermédiaire","Integrate AI APIs into core workflows",(8000,20000)),
              (90,"Avancé","Build custom AI agents for key processes",(20000,50000)),
              (101,"Expert","Scale and optimize existing AI systems",(50000,200000))]
    level, rec, budget = next((l,r,b) for t,l,r,b in levels if score <= t)
    return jsonify({"score": score, "level": level, "recommendation": rec,
                    "estimated_ai_budget_eur": {"min": budget[0], "max": budget[1]},
                    "criteria": criteria, "criteria_met": sum(criteria.values())})

@app.route('/pitch-generator', methods=['GET','POST'])
def pitch_generator():
    d = get_data()
    expertise = d.get('expertise', 'AI consultant')
    target = d.get('target', 'startups')
    result = d.get('result', 'save time')
    metric = d.get('metric', '40%')
    lang = d.get('lang', 'fr')
    if lang == 'fr':
        pitch = f"J'aide les {target} à {result} grâce à mon expertise en {expertise}. Mes clients gagnent en moyenne {metric} de temps sur leurs tâches opérationnelles. Je prends 3 clients maximum pour garantir des résultats concrets en 2 semaines."
    else:
        pitch = f"I help {target} to {result} through my {expertise} expertise. My clients save an average of {metric} on operational tasks. I work with max 3 clients to guarantee concrete results within 2 weeks."
    return jsonify({"pitch": pitch, "words": len(pitch.split()), "lang": lang,
                    "linkedin_ready": len(pitch) < 700})

@app.route('/invoice-calculator', methods=['GET','POST'])
def invoice_calculator():
    d = get_data()
    days = float(d.get('days_worked', 1))
    tjm = float(d.get('tjm', 500))
    vat_rate = float(d.get('vat_rate', 20))
    discount = float(d.get('discount_percent', 0))
    subtotal = days * tjm
    after_discount = subtotal * (1 - discount/100)
    vat = after_discount * vat_rate / 100
    total = after_discount + vat
    return jsonify({
        "days_worked": days, "tjm_eur": tjm,
        "subtotal_eur": round(subtotal, 2),
        "discount_eur": round(subtotal - after_discount, 2),
        "vat_eur": round(vat, 2),
        "total_eur": round(total, 2),
        "total_formatted": f"{total:,.2f}€"
    })

@app.route('/project-estimator', methods=['GET','POST'])
def project_estimator():
    d = get_data()
    complexity = d.get('complexity', 'medium')
    project_type = d.get('type', 'website')
    features = int(d.get('features', 5))
    base_days = {'simple':3,'medium':10,'complex':25,'enterprise':60}.get(complexity, 10)
    type_mult = {'website':1.0,'mobile':1.4,'api':0.8,'ai':1.6,'automation':1.2,'saas':2.0}.get(project_type, 1.0)
    days = round(base_days * type_mult * (1 + features * 0.1))
    buffer = round(days * 0.25)
    return jsonify({
        "project_type": project_type, "complexity": complexity,
        "estimated_days": days, "with_buffer_days": days + buffer,
        "recommended_quote_eur": {"low": days * 400, "mid": days * 600, "high": days * 900},
        "tip": f"Add {buffer} days buffer for revisions and testing"
    })

@app.route('/keyword-extractor', methods=['GET','POST'])
def keyword_extractor():
    d = get_data()
    text = d.get('text', '')
    if not text:
        return jsonify({"error": "Provide 'text' parameter"}), 400
    words = re.findall(r'\b[a-zA-ZÀ-ÿ]{4,}\b', text.lower())
    stopwords = {'dans','avec','pour','vous','nous','les','des','une','est','pas','plus','sur','par','qui','que','cette','votre','notre','leur','leurs','tout','mais','comme','aussi'}
    freq = {}
    for w in words:
        if w not in stopwords: freq[w] = freq.get(w, 0) + 1
    keywords = sorted(freq.items(), key=lambda x: -x[1])[:15]
    return jsonify({"keywords": [{"word":k,"count":v} for k,v in keywords],
                    "word_count": len(words), "unique_words": len(freq)})

@app.route('/seo-score', methods=['GET','POST'])
def seo_score():
    d = get_data()
    title = d.get('title','')
    description = d.get('description','')
    content = d.get('content','')
    keyword = d.get('keyword','')
    checks = {
        'title_length': 40 <= len(title) <= 60,
        'description_length': 120 <= len(description) <= 160,
        'keyword_in_title': keyword.lower() in title.lower() if keyword else False,
        'keyword_in_description': keyword.lower() in description.lower() if keyword else False,
        'content_length': len(content) >= 300,
        'keyword_density': (content.lower().count(keyword.lower()) / max(len(content.split()),1) * 100 if keyword else 0) >= 0.5,
    }
    score = round(sum(checks.values()) / len(checks) * 100)
    return jsonify({"seo_score": score, "checks": checks,
                    "recommendation": "Good SEO!" if score >= 80 else "Add keyword to title and description"})

@app.route('/reading-time', methods=['GET','POST'])
def reading_time():
    d = get_data()
    text = d.get('text','')
    words = len(text.split())
    minutes = round(words / 200)
    return jsonify({"words": words, "reading_time_minutes": max(1, minutes),
                    "characters": len(text)})

@app.route('/currency-converter', methods=['GET','POST'])
def currency_converter():
    d = get_data()
    amount = float(d.get('amount', 100))
    from_curr = d.get('from', 'EUR').upper()
    to_curr = d.get('to', 'USD').upper()
    rates_to_eur = {'EUR':1.0,'USD':0.926,'GBP':1.176,'CHF':1.042,'CAD':0.685,'AUD':0.607,'JPY':0.0062}
    rate_from = rates_to_eur.get(from_curr, 1.0)
    rate_to = rates_to_eur.get(to_curr, 1.0)
    result = amount * rate_from / rate_to
    return jsonify({"amount": amount, "from": from_curr, "to": to_curr,
                    "result": round(result, 2), "rate": round(rate_from/rate_to, 4),
                    "note": "Approximate rates, updated manually"})

@app.route('/health')
def health():
    return jsonify({"status": "ok", "version": "2.0.0", "endpoints": 12,
                    "timestamp": datetime.utcnow().isoformat()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
