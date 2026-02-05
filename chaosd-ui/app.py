from flask import Flask, render_template, request, jsonify
import subprocess
import docker
import os
import uuid

app = Flask(__name__)

# Initialize Docker client
docker_client = docker.from_env()

# Store active experiments
experiments = {}

def run_chaosd_command(cmd_args):
    """Execute a chaosd command via docker exec"""
    try:
        container = docker_client.containers.get('orion_chaosd')
        result = container.exec_run(['chaosd'] + cmd_args)
        return result.output.decode('utf-8'), result.exit_code
    except Exception as e:
        return str(e), 1

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/experiments', methods=['GET'])
def get_experiments():
    """Récupère la liste des expériences en cours"""
    return jsonify(list(experiments.values()))

@app.route('/api/containers', methods=['GET'])
def list_containers():
    """Liste uniquement les conteneurs audiomancy (backend, frontend, mongodb)"""
    try:
        # Lister tous les conteneurs en cours d'exécution
        containers = docker_client.containers.list(all=False)
        container_list = []

        for c in containers:
            # Récupérer les réseaux du conteneur
            networks = list(c.attrs['NetworkSettings']['Networks'].keys())
            network_display = ', '.join(networks) if networks else 'default'

            # Filtrer uniquement les conteneurs audiomancy (nom commence par "audiomancy-")
            if c.name.startswith('audiomancy-'):
                container_list.append({
                    'id': c.id[:12],
                    'name': c.name,
                    'status': c.status,
                    'image': c.image.tags[0] if c.image.tags else 'unknown',
                    'networks': networks,
                    'network_display': network_display
                })

        # Trier par nom pour une meilleure lisibilité
        container_list.sort(key=lambda x: x['name'])

        return jsonify(container_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/attack/container-kill', methods=['POST'])
def attack_container_kill():
    """Tue un conteneur Docker"""
    data = request.json
    container_id = data.get('container_id', '')
    signal = data.get('signal', 'SIGKILL')

    if not container_id:
        return jsonify({'error': 'container_id is required'}), 400

    try:
        # Use Docker Python API
        container = docker_client.containers.get(container_id)
        container.kill(signal=signal)

        exp_id = str(uuid.uuid4())
        experiments[exp_id] = {
            'uid': exp_id,
            'kind': f'container-kill ({signal})',
            'status': 'completed',
            'target': container_id
        }

        return jsonify({'uid': exp_id, 'status': 'success', 'message': f'Container {container_id} killed'})
    except docker.errors.NotFound:
        return jsonify({'error': f'Container {container_id} not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/attack/container-stop', methods=['POST'])
def attack_container_stop():
    """Arrête un conteneur Docker"""
    data = request.json
    container_id = data.get('container_id', '')

    if not container_id:
        return jsonify({'error': 'container_id is required'}), 400

    try:
        # Use Docker Python API
        container = docker_client.containers.get(container_id)
        container.stop()

        exp_id = str(uuid.uuid4())
        experiments[exp_id] = {
            'uid': exp_id,
            'kind': 'container-stop',
            'status': 'completed',
            'target': container_id
        }

        return jsonify({'uid': exp_id, 'status': 'success', 'message': f'Container {container_id} stopped'})
    except docker.errors.NotFound:
        return jsonify({'error': f'Container {container_id} not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/attack/stress-cpu', methods=['POST'])
def attack_stress_cpu():
    """Stress CPU via Chaosd"""
    data = request.json
    workers = data.get('workers', 2)
    load = data.get('load', 100)

    # Use chaosd CLI via docker exec
    cmd_args = ['attack', 'stress', 'cpu', '--workers', str(workers), '--load', str(load)]
    output, returncode = run_chaosd_command(cmd_args)

    if returncode != 0:
        return jsonify({'error': output or 'Failed to start CPU stress'}), 500

    # Extract UID from output if possible
    exp_id = str(uuid.uuid4())
    for line in output.split('\n'):
        if 'Attack stress successfully' in line or 'uid' in line.lower():
            # Try to extract UID
            parts = line.split()
            for i, part in enumerate(parts):
                if 'uid' in part.lower() and i + 1 < len(parts):
                    exp_id = parts[i + 1].strip(':,')
                    break

    experiments[exp_id] = {
        'uid': exp_id,
        'kind': f'stress-cpu (workers={workers}, load={load}%)',
        'status': 'running',
        'target': 'localhost'
    }

    return jsonify({'uid': exp_id, 'status': 'success', 'message': 'CPU stress started'})

@app.route('/api/attack/stress-memory', methods=['POST'])
def attack_stress_memory():
    """Stress Memory via Chaosd"""
    data = request.json
    size = data.get('size', '256MB')

    # Use chaosd CLI via docker exec
    cmd_args = ['attack', 'stress', 'mem', '--size', size]
    output, returncode = run_chaosd_command(cmd_args)

    if returncode != 0:
        return jsonify({'error': output or 'Failed to start memory stress'}), 500

    exp_id = str(uuid.uuid4())
    experiments[exp_id] = {
        'uid': exp_id,
        'kind': f'stress-memory (size={size})',
        'status': 'running',
        'target': 'localhost'
    }

    return jsonify({'uid': exp_id, 'status': 'success', 'message': 'Memory stress started'})

@app.route('/api/attack/network-delay', methods=['POST'])
def attack_network_delay():
    """Ajoute de la latence réseau via Chaosd"""
    data = request.json
    latency = data.get('latency', '100ms')
    jitter = data.get('jitter', '10ms')
    device = data.get('device', 'eth0')

    # Use chaosd CLI via docker exec
    cmd_args = ['attack', 'network', 'delay', '--latency', latency, '--jitter', jitter, '--device', device]
    output, returncode = run_chaosd_command(cmd_args)

    if returncode != 0:
        return jsonify({'error': output or 'Failed to add network delay'}), 500

    exp_id = str(uuid.uuid4())
    experiments[exp_id] = {
        'uid': exp_id,
        'kind': f'network-delay (latency={latency}, jitter={jitter})',
        'status': 'running',
        'target': device
    }

    return jsonify({'uid': exp_id, 'status': 'success', 'message': 'Network delay added'})

@app.route('/api/attack/network-loss', methods=['POST'])
def attack_network_loss():
    """Simule une perte de paquets réseau via Chaosd"""
    data = request.json
    percent = data.get('percent', 10)
    device = data.get('device', 'eth0')

    # Use chaosd CLI via docker exec
    cmd_args = ['attack', 'network', 'loss', '--percent', str(percent), '--device', device]
    output, returncode = run_chaosd_command(cmd_args)

    if returncode != 0:
        return jsonify({'error': output or 'Failed to add network loss'}), 500

    exp_id = str(uuid.uuid4())
    experiments[exp_id] = {
        'uid': exp_id,
        'kind': f'network-loss (percent={percent}%)',
        'status': 'running',
        'target': device
    }

    return jsonify({'uid': exp_id, 'status': 'success', 'message': 'Network loss started'})

@app.route('/api/recover/<uid>', methods=['DELETE'])
def recover_experiment(uid):
    """Arrête une expérience et redémarre les conteneurs si nécessaire"""
    if uid not in experiments:
        return jsonify({'error': 'Experiment not found'}), 404

    experiment = experiments[uid]

    # Si c'est une expérience de conteneur, redémarrer le conteneur
    if 'container' in experiment['kind'].lower():
        try:
            container_id = experiment['target']
            container = docker_client.containers.get(container_id)

            # Redémarrer le conteneur s'il est arrêté
            if container.status != 'running':
                container.start()
        except Exception as e:
            # Log l'erreur mais continue
            print(f"Erreur lors du redémarrage du conteneur: {e}")

    # Pour les autres types d'expériences, utiliser chaosd recover
    if 'stress' in experiment['kind'].lower() or 'network' in experiment['kind'].lower():
        cmd_args = ['recover', uid]
        output, returncode = run_chaosd_command(cmd_args)

    # Remove from experiments
    experiments.pop(uid, None)

    return jsonify({'status': 'success', 'message': f'Experiment {uid} recovered'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
