import math
import requests
import json
from bs4 import BeautifulSoup
from urllib.parse import quote as encode
from datetime import datetime, timedelta
from time import sleep

# Constantes
INIT_URL = 'https://www.linkedin.com/jobs/search'
PAGE_URL = 'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search'
POST_URL = 'https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/'
HEADERS = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"}

# Variáveis globais para armazenar o estado da busca
search_status = {
    "is_searching": False,
    "progress": 0,
    "status_message": "Pronto para iniciar",
    "log_messages": [],
    "results": [],
    "total_jobs": 0,
    "collected_jobs": 0
}

def log_message(message):
    timestamp = datetime.now().strftime('%H:%M:%S')
    log_entry = f"{timestamp} - {message}"
    search_status["log_messages"].append(log_entry)
    print(log_entry)

def update_progress(progress, message):
    search_status["progress"] = progress
    search_status["status_message"] = message
    log_message(message)

def calculate_time_range(max_date):
    if not max_date:
        return 'r86400'  # Default: 24 horas
    
    max_date = datetime.strptime(max_date, '%Y-%m-%d')
    delta = datetime.now() - max_date
    return f"r{int(delta.total_seconds())}"

def build_params(keywords, location, time_range, distance, job_type, place, start=0):
    params = [
        ('f_TPR', time_range),
        ('position', '1'),
        ('pageNum', '0'),
        ('start', str(start)),
        ('sortBy', 'DD')
    ]
    
    if keywords: params.append(('keywords', encode(keywords)))
    if location: params.append(('location', encode(location)))
    if distance: params.append(('distance', distance))
    if job_type: params.append(('f_JT', ','.join(job_type)))
    if place: params.append(('f_WT', ','.join(place)))
    
    return '?' + '&'.join([f"{k}={v}" for k, v in params])

def get_job_count(keywords, location, time_range, distance, job_type, place, limit_jobs):
    if limit_jobs > 0:
        return limit_jobs

    try:
        uri = INIT_URL + build_params(keywords, location, time_range, distance, job_type, place)
        log_message(f"Consultando: {uri}")
        res = requests.get(uri, headers=HEADERS)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        job_count_element = (soup.find('span', {'class': 'results-context-header__job-count'}) or 
                            soup.find('span', {'class': 'results-context-header__new-jobs'}))
        
        if job_count_element:
            job_count = job_count_element.text.strip().replace(",", "").replace("+", "")
            return min(int(job_count), 1000)  # Limite máximo de segurança
        return 1000  # Default se não encontrar contagem
    
    except Exception as e:
        log_message(f"Erro ao obter contagem de vagas: {e}")
        return 1000  # Default para continuar a execução

def get_job_ids_per_page(keywords, location, time_range, distance, job_type, place, start):
    try:
        if not search_status["is_searching"]:
            return []
                
        uri = PAGE_URL + build_params(keywords, location, time_range, distance, job_type, place, start)
        res = requests.get(uri, headers=HEADERS, timeout=30)
        
        if res.status_code == 404:
            return []
                
        if not res.ok:
            log_message(f"Tentando novamente a página {start}...")
            sleep(2)
            return get_job_ids_per_page(keywords, location, time_range, distance, job_type, place, start)

        soup = BeautifulSoup(res.text, 'html.parser')
        return [li.find('div')['data-entity-urn'].split(':')[-1] 
                for li in soup.find_all('li') 
                if li.find('div') and li.find('div').has_attr('data-entity-urn')]
                    
    except Exception as e:
        log_message(f"Falha na página {start}: {e}")
        sleep(1)
        return []

def get_job_detail(job_id):
    try:
        if not search_status["is_searching"]:
            return {}
                
        uri = POST_URL + job_id
        res = requests.get(uri, headers=HEADERS, timeout=30)
        res.raise_for_status()
        
        soup = BeautifulSoup(res.text, 'html.parser')
        detail = {
            'title': soup.find('h2', {'class': 'top-card-layout__title'}).get_text(strip=True) if soup.find('h2', {'class': 'top-card-layout__title'}) else None,
            'company': soup.find('a', {'class': 'topcard__org-name-link'}).get_text(strip=True) if soup.find('a', {'class': 'topcard__org-name-link'}) else None,
            'location': soup.find('span', {'class': 'topcard__flavor--bullet'}).get_text(strip=True) if soup.find('span', {'class': 'topcard__flavor--bullet'}) else None,
            'id': job_id,
            'link': uri,
            'description': (soup.find('div', {'class': 'show-more-less-html__markup'}).get_text(strip=True) 
                          if soup.find('div', {'class': 'show-more-less-html__markup'}) else None),
            'time': soup.find('span', {'class': 'posted-time-ago__text'}).get_text(strip=True) if soup.find('span', {'class': 'posted-time-ago__text'}) else None,
        }

        criterias = soup.find_all('li', {'class': 'description__job-criteria-item'})
        for crit in criterias:
            key = crit.find('h3').get_text(strip=True)
            value = crit.find('span').get_text(strip=True)
            detail[key] = value
                
        return detail
        
    except Exception as e:
        log_message(f"Falha na vaga {job_id}: {e}")
        return {'id': job_id, 'error': str(e)}

def search_jobs_thread(keywords, location, max_date, distance, job_type, place, limit_jobs):
    search_status["is_searching"] = True
    search_status["progress"] = 0
    search_status["log_messages"] = []
    search_status["results"] = []
    
    try:
        # Calcular intervalo de tempo
        time_range = calculate_time_range(max_date)
        
        # Passo 1: Obter número total de vagas
        log_message("Obtendo número total de vagas...")
        total_jobs = get_job_count(keywords, location, time_range, distance, job_type, place, limit_jobs)
        num_pages = math.ceil(total_jobs / 25)
        log_message(f"Encontradas ~{total_jobs} vagas ({num_pages} páginas)")
        search_status["total_jobs"] = total_jobs
        
        # Passo 2: Coletar IDs de vagas
        job_ids = []
        for page in range(num_pages):
            if not search_status["is_searching"]:
                break
                
            new_ids = get_job_ids_per_page(keywords, location, time_range, distance, job_type, place, page * 25)
            job_ids += new_ids
            
            progress = (page + 1) / num_pages * 50  # Primeiros 50% do progresso
            update_progress(progress, f"Coletando páginas: {page+1}/{num_pages} ({len(job_ids)} IDs)")
            sleep(0.1)
        
        if not search_status["is_searching"]:
            log_message("Busca interrompida pelo usuário")
            search_status["status_message"] = "Busca interrompida"
            search_status["is_searching"] = False
            return
        
        # Limitar número de vagas se necessário
        if limit_jobs > 0:
            job_ids = job_ids[:limit_jobs]
        
        # Passo 3: Obter detalhes de cada vaga
        jobs = []
        for i, job_id in enumerate(job_ids):
            if not search_status["is_searching"]:
                break
                
            job_detail = get_job_detail(job_id)
            if job_detail and not job_detail.get('error'):
                jobs.append(job_detail)
                search_status["results"] = jobs  # Atualizar resultados em tempo real
            
            progress = 50 + (i + 1) / len(job_ids) * 50  # Últimos 50% do progresso
            update_progress(progress, f"Obtendo detalhes: {i+1}/{len(job_ids)} ({len(jobs)} vagas)")
            search_status["collected_jobs"] = len(jobs)
            sleep(0.2)
        
        # Finalizar
        if search_status["is_searching"]:
            log_message(f"✅ {len(jobs)} vagas coletadas com sucesso")
            search_status["status_message"] = f"Concluído: {len(jobs)} vagas encontradas"
            search_status["progress"] = 100
        
    except Exception as e:
        log_message(f"❌ Erro: {e}")
        search_status["status_message"] = f"Erro: {str(e)}"
    
    search_status["is_searching"] = False