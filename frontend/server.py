from flask import Flask, render_template

# On définit le dossier courant comme dossier de templates
app = Flask(__name__, template_folder='.') 

@app.route('/inventory')
def inventory_page():
    # Flask va chercher dans le dossier courant, donc on précise 'inventory/index.html'
    return render_template('inventory/index.html')

if __name__ == '__main__':
    # Écoute sur 0.0.0.0 pour être accessible depuis l'extérieur du conteneur Docker
    app.run(host='0.0.0.0', port=8080, debug=True)