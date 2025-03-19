from flask import Flask, render_template, request, jsonify, Response
import threading
import io
import csv
import json
from datetime import datetime
from scraper import search_jobs_thread, search_status

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    if search_status["is_searching"]:
        return jsonify({"error": "Já existe uma busca em andamento"}), 400
    
    # Obter parâmetros
    data = request.json
    keywords = data.get('keywords', '')
    location = data.get('location', '')
    max_date = data.get('max_date', '')
    distance = data.get('distance', '')
    job_type = data.get('job_type', [])
    place = data.get('place', [])
    limit_jobs = int(data.get('limit_jobs', 100))
    
    # Iniciar thread de busca
    thread = threading.Thread(
        target=search_jobs_thread, 
        args=(keywords, location, max_date, distance, job_type, place, limit_jobs)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({"message": "Busca iniciada"}), 200

@app.route('/stop', methods=['POST'])
def stop_search():
    search_status["is_searching"] = False
    return jsonify({"message": "Busca interrompida"}), 200

@app.route('/status')
def get_status():
    return jsonify(search_status)

@app.route('/results')
def get_results():
    return jsonify(search_status["results"])

@app.route('/job/<job_id>')
def get_job(job_id):
    # Encontrar a vaga específica
    job = next((job for job in search_status["results"] if job.get('id') == job_id), None)
    
    if job:
        return jsonify(job)
    else:
        return jsonify({"error": "Vaga não encontrada"}), 404

@app.route('/export/csv')
def export_csv():
    if not search_status["results"]:
        return jsonify({"error": "Nenhum resultado disponível para exportar"}), 400
    
    # Criar arquivo CSV em memória
    output = io.StringIO()
    all_keys = set()
    for job in search_status["results"]:
        all_keys.update(job.keys())
    
    if 'error' in all_keys:
        all_keys.remove('error')
    
    fieldnames = sorted(all_keys)
    
    for field in ['id', 'title', 'company', 'location', 'time', 'link', 'description']:
        if field in fieldnames:
            fieldnames.remove(field)
            fieldnames.insert(0, field)
    
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore')
    writer.writeheader()
    for job in search_status["results"]:
        # Filtrar jobs que têm erro
        if not job.get('error'):
            writer.writerow(job)
    
    output.seek(0)
    filename = f"vagas_linkedin_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )

@app.route('/export/json')
def export_json():
    if not search_status["results"]:
        return jsonify({"error": "Nenhum resultado disponível para exportar"}), 400
    
    valid_jobs = [job for job in search_status["results"] if not job.get('error')]
    
    filename = f"vagas_linkedin_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    return Response(
        json.dumps(valid_jobs, ensure_ascii=False, indent=2),
        mimetype="application/json",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )

if __name__ == '__main__':
    app.run(debug=True)