from flask import Flask, request, jsonify
import os

app = Flask(__name__)

def get_data():
    """Récupère les données depuis GET params ou POST JSON"""
    if request.method == 'POST' and request.is_json:
        return request.get_json()
    return request.args.to_dict()

@app.route('/')
def home():
    return jsonify({
        "name": "OpenMind Freelance Tools API",
        "version": "1.0.0",
        "endpoints": {
            "/rate-calculator": "Calculate ideal freelance daily/hourly rate",
            "/ai-audit-score": "AI maturity score for a company",
            "/pitch-generator": "Generate a 3-sentence freelance pitch"
        },
        "store": "https://oopenmind710-pixel.github.io/openmind-store/"
    })

@app.route('/rate-calculator', methods=['GET', 'POST'])
def rate_calculator():
    d = get_data()
    annual = float(d.get('annual_target', 60000))
    vacation = int(d.get('weeks_vacation', 5))
    hours = float(d.get('hours_per_day', 7))
    overhead = float(d.get('overhead_percent', 30))
    expertise = d.get('expertise', 'mid')
    
    working_days = (52 - vacation) * 5
    with_overhead = annual * (1 + overhead / 100)
    mult = {'junior': 0.8, 'mid': 1.0, 'senior': 1.3, 'expert': 1.6}.get(expertise, 1.0)
    tjm = round((with_overhead / working_days) * mult)
    
    return jsonify({
        "annual_target_eur": annual,
        "tjm_eur": tjm,
        "hourly_eur": round(tjm / hours),
        "monthly_eur": round(tjm * 20),
        "working_days": working_days,
        "expertise": expertise
    })

@app.route('/ai-audit-score', methods=['GET', 'POST'])
def ai_audit_score():
    d = get_data()
    criteria = {
        'has_automation': d.get('has_automation','').lower() in ['true','1','yes'],
        'uses_ai_tools': d.get('uses_ai_tools','').lower() in ['true','1','yes'],
        'data_structured': d.get('data_structured','').lower() in ['true','1','yes'],
        'team_trained': d.get('team_trained','').lower() in ['true','1','yes'],
        'has_ai_strategy': d.get('has_ai_strategy','').lower() in ['true','1','yes'],
        'budget_allocated': d.get('budget_allocated','').lower() in ['true','1','yes'],
    }
    score = sum(criteria.values()) * 100 // len(criteria)
    levels = [(20,"Débutant","Automatiser 1 processus répétitif"), (40,"Explorateur","Former l'équipe aux outils IA"),
              (60,"Intermédiaire","Intégrer des APIs IA"), (80,"Avancé","Développer des agents IA"), (101,"Expert","Scale les systèmes IA")]
    level, rec = next((l,r) for t,l,r in levels if score < t)
    return jsonify({"score": score, "level": level, "recommendation": rec, "criteria": criteria})

@app.route('/pitch-generator', methods=['GET', 'POST'])
def pitch_generator():
    d = get_data()
    expertise = d.get('expertise', 'développeur')
    target = d.get('target', 'startups')
    result = d.get('result', 'gagner du temps')
    return jsonify({
        "pitch_fr": f"J'aide les {target} à {result} grâce à mon expertise en {expertise}. En moyenne, mes clients voient des résultats en 2 semaines. Je travaille avec 3 clients max pour garantir la qualité.",
        "pitch_en": f"I help {target} to {result} through my {expertise} expertise. On average, clients see results within 2 weeks. I work with max 3 clients for top quality.",
    })

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
