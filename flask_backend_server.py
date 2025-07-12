from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import pandas as pd
from datetime import datetime, timedelta
import json

import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns
from io import BytesIO
import tempfile
import os
from collections import defaultdict

# Email configuration (add these constants after the imports)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "ahmedmtawahg@gmail.com"    # Replace with your app password
EMAIL_PASSWORD = "wdiervjootstklaq"  # Replace with your email


app = Flask(__name__)
CORS(app)  # Permet les requêtes cross-origin depuis le frontend

@app.route('/api/connect', methods=['POST'])
def connect_and_fetch_data():
    try:
        # Récupération des paramètres de connexion depuis le frontend
        data = request.json
        db_config = {
            "host": data.get('host', 'localhost'),
            "user": data.get('user', 'root'),
            "password": data.get('password', 'azerty'),
            "database": data.get('database', 'scheduler_test'),
            "port": data.get('port', 3306)
        }
        
        date_debut = data.get('startDate', '2025-05-01')
        date_fin = data.get('endDate', '2025-05-31')
        
        # Connexion MySQL
        print(f"Tentative de connexion à {db_config['host']}:{db_config['port']}")
        conn = pymysql.connect(**db_config)
        
        # Récupération des données
        query = """
SELECT JOB_NAME, START_TIME, END_TIME
FROM stg_scheduler_history
WHERE START_TIME BETWEEN %s AND %s
  AND END_TIME IS NOT NULL
"""
        """
        SELECT JOB_NAME, START_TIME, END_TIME
        FROM stg_scheduler_history
        WHERE START_TIME IS NOT NULL AND END_TIME IS NOT NULL
        """
        
        print("Exécution de la requête SQL...")
        df = pd.read_sql(query, conn, params=[date_debut, date_fin])
        # df = pd.read_sql(query, conn)
        conn.close()
        
        print(f"Récupération de {len(df)} enregistrements")
        
        # Nettoyage et calcul des durées
        df["START_TIME"] = pd.to_datetime(df["START_TIME"], errors='coerce')
        df["END_TIME"] = pd.to_datetime(df["END_TIME"], errors='coerce')
        df["DURATION"] = (df["END_TIME"] - df["START_TIME"]).dt.total_seconds() / 60
        df["DURATION"] = df["DURATION"].fillna(0)
        df["DATE"] = df["START_TIME"].dt.date
        
        # Filtrer la période demandée
        start_date = pd.to_datetime(date_debut).date()
        end_date = pd.to_datetime(date_fin).date()
        df_filtered = df[(df["DATE"] >= start_date) & (df["DATE"] <= end_date)]
        
        print(f"Données filtrées: {len(df_filtered)} enregistrements pour la période {start_date} à {end_date}")
        
        # Conversion en format JSON pour le frontend
        result_data = []
        for _, row in df_filtered.iterrows():
            if pd.notna(row['JOB_NAME']) and pd.notna(row['START_TIME']) and pd.notna(row['END_TIME']):
                result_data.append({
                    'jobName': row['JOB_NAME'],
                    'startTime': row['START_TIME'].isoformat(),
                    'endTime': row['END_TIME'].isoformat(),
                    'duration': float(row['DURATION']),
                    'date': row['DATE'].isoformat()
                })
        
        return jsonify({
            'success': True,
            'data': result_data,
            'message': f'✅ {len(result_data)} jobs récupérés avec succès',
            'total_records': len(df),
            'filtered_records': len(df_filtered)
        })
        
    except pymysql.Error as e:
        print(f"Erreur MySQL: {e}")
        return jsonify({
            'success': False,
            'error': f'Erreur de connexion MySQL: {str(e)}',
            'message': '❌ Échec de la connexion à la base de données'
        }), 500
        
    except Exception as e:
        print(f"Erreur générale: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '❌ Erreur lors du traitement des données'
        }), 500

@app.route('/api/test', methods=['GET'])
def test_connection():
    return jsonify({
        'success': True,
        'message': 'Serveur Flask fonctionnel',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/generate-pdf', methods=['POST'])
def generate_pdf():
    try:
        data = request.json
        pdf_type = data.get('type')
        
        # Create a temporary file for the PDF
        temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_pdf.close()
        
        if pdf_type == 'single':
            job_name = data.get('jobName')
            job_data = data.get('jobData')
            generate_single_job_pdf(temp_pdf.name, job_name, job_data)
        elif pdf_type == 'all':
            all_jobs_data = data.get('allJobsData')
            generate_all_jobs_pdf(temp_pdf.name, all_jobs_data)
        else:
            return jsonify({'success': False, 'error': 'Type de PDF invalide'}), 400
        
        # Return the PDF as a file download
        def remove_file(response):
            try:
                os.unlink(temp_pdf.name)
            except Exception:
                pass
            return response
        
        from flask import send_file
        response = send_file(temp_pdf.name, as_attachment=True, 
                           download_name=f'job_analysis_{pdf_type}.pdf',
                           mimetype='application/pdf')
        response.call_on_close(remove_file)
        return response
        
    except Exception as e:
        print(f"Erreur génération PDF: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/send-email', methods=['POST'])
def send_email():
    try:
        data = request.json
        email_type = data.get('type')
        recipient_email = data.get('email')
        subject = data.get('subject')
        message = data.get('message', '')
        
        # Generate PDF
        temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_pdf.close()
        
        if email_type == 'single':
            job_name = data.get('jobName')
            job_data = data.get('jobData')
            generate_single_job_pdf(temp_pdf.name, job_name, job_data)
            filename = f"analysis_{job_name.replace('/', '_')}.pdf"
        elif email_type == 'all':
            all_jobs_data = data.get('allJobsData')
            generate_all_jobs_pdf(temp_pdf.name, all_jobs_data)
            filename = "analysis_all_jobs.pdf"
        else:
            return jsonify({'success': False, 'error': 'Type d\'email invalide'}), 400
        
        # Send email with PDF attachment
        send_email_with_attachment(recipient_email, subject, message, temp_pdf.name, filename)
        
        # Clean up
        os.unlink(temp_pdf.name)
        
        return jsonify({'success': True, 'message': 'Email envoyé avec succès'})
        
    except Exception as e:
        print(f"Erreur envoi email: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def generate_single_job_pdf(filename, job_name, job_data):
    """Generate PDF for a single job"""
    plt.style.use('seaborn-v0_8')
    
    with PdfPages(filename) as pdf:
        # Convert job data
        dates = []
        durations = []
        daily_data = defaultdict(float)
        
        for job in job_data:
            date = pd.to_datetime(job['date']).date()
            duration = job['duration']
            daily_data[date] += duration
        
        dates = sorted(daily_data.keys())
        durations = [daily_data[date] for date in dates]
        
        # Calculate statistics
        avg_duration = sum(durations) / len(durations) if durations else 0
        max_duration = max(durations) if durations else 0
        min_duration = min(durations) if durations else 0
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Plot data
        ax.plot(dates, durations, marker='o', linewidth=2, markersize=6, 
                color='#3498db', label='Durée quotidienne')
        
        # Add reference lines
        ax.axhline(y=avg_duration, color='orange', linestyle='--', alpha=0.7, 
                   label=f'Moyenne: {avg_duration:.1f} min')
        ax.axhline(y=max_duration, color='red', linestyle='--', alpha=0.7, 
                   label=f'Maximum: {max_duration:.1f} min')
        ax.axhline(y=min_duration, color='green', linestyle='--', alpha=0.7, 
                   label=f'Minimum: {min_duration:.1f} min')
        
        # Formatting
        ax.set_title(f'Analyse de Performance - {job_name}', fontsize=16, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Durée (minutes)', fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Format x-axis dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates)//10)))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # Add statistics page
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.axis('off')
        
        stats_text = f"""
Rapport d'Analyse - {job_name}
{'='*50}

Statistiques générales:
• Nombre total d'exécutions: {len(job_data)}
• Durée moyenne: {avg_duration:.2f} minutes
• Durée maximum: {max_duration:.2f} minutes  
• Durée minimum: {min_duration:.2f} minutes
• Période analysée: {min(dates)} au {max(dates)}

Détails par jour:
"""
        
        for date, duration in zip(dates, durations):
            stats_text += f"• {date}: {duration:.1f} min\n"
        
        ax.text(0.1, 0.9, stats_text, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', fontfamily='monospace')
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

def generate_all_jobs_pdf(filename, all_jobs_data):
    """Generate PDF for all jobs"""
    plt.style.use('seaborn-v0_8')
    
    # Group jobs by name
    jobs_grouped = defaultdict(list)
    for job in all_jobs_data:
        jobs_grouped[job['jobName']].append(job)
    
    with PdfPages(filename) as pdf:
        # Summary page
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.axis('off')
        
        summary_text = f"""
Rapport d'Analyse Complet - Tous les Jobs
{'='*60}

Résumé général:
• Nombre total de jobs: {len(jobs_grouped)}
• Nombre total d'exécutions: {len(all_jobs_data)}
• Période d'analyse: {min(job['date'] for job in all_jobs_data)} au {max(job['date'] for job in all_jobs_data)}

Liste des jobs analysés:
"""
        
        for job_name, job_data in jobs_grouped.items():
            durations = [job['duration'] for job in job_data]
            avg_duration = sum(durations) / len(durations)
            summary_text += f"• {job_name}: {len(job_data)} exécutions, {avg_duration:.1f} min (moyenne)\n"
        
        ax.text(0.05, 0.95, summary_text, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', fontfamily='monospace')
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # Generate a chart for each job
        for job_name, job_data in jobs_grouped.items():
            # Aggregate by date
            daily_data = defaultdict(float)
            for job in job_data:
                date = pd.to_datetime(job['date']).date()
                daily_data[date] += job['duration']
            
            dates = sorted(daily_data.keys())
            durations = [daily_data[date] for date in dates]
            
            if not durations:
                continue
                
            # Calculate statistics
            avg_duration = sum(durations) / len(durations)
            max_duration = max(durations)
            min_duration = min(durations)
            
            # Create plot
            fig, ax = plt.subplots(figsize=(12, 6))
            
            ax.plot(dates, durations, marker='o', linewidth=2, markersize=4, 
                    color='#3498db', label='Durée quotidienne')
            
            ax.axhline(y=avg_duration, color='orange', linestyle='--', alpha=0.7, 
                       label=f'Moyenne: {avg_duration:.1f} min')
            
            ax.set_title(f'{job_name}', fontsize=12, fontweight='bold')
            ax.set_xlabel('Date', fontsize=10)
            ax.set_ylabel('Durée (min)', fontsize=10)
            ax.legend(fontsize=9)
            ax.grid(True, alpha=0.3)
            
            # Format dates
            if len(dates) > 10:
                ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates)//8)))
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, fontsize=8)
            
            plt.tight_layout()
            pdf.savefig(fig, bbox_inches='tight')
            plt.close()

def send_email_with_attachment(recipient_email, subject, message, attachment_path, attachment_name):
    """Send email with PDF attachment"""
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = recipient_email
    msg['Subject'] = subject
    
    # Add body to email
    body = f"""
{message}

Ce rapport a été généré automatiquement par l'Analyseur de Performance des Jobs.

Cordialement,
Système d'Analyse des Jobs
"""
    
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    # Attach PDF
    with open(attachment_path, "rb") as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
    
    encoders.encode_base64(part)
    part.add_header(
        'Content-Disposition',
        f'attachment; filename= {attachment_name}',
    )
    
    msg.attach(part)
    
    # Send email
    context = ssl.create_default_context()
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls(context=context)
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)

if __name__ == '__main__':
    print("🚀 Démarrage du serveur Flask...")
    print("📊 API disponible sur http://localhost:5000")
    print("🔗 Endpoints:")
    print("   - POST /api/connect : Connexion et récupération des données")
    print("   - GET /api/test : Test de connexion")
    print("   - POST /api/generate-pdf : Génération de PDF") 
    print("   - POST /api/send-email : Envoi d'email avec PDF")
    app.run(debug=True, host='0.0.0.0', port=5000)