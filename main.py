import base64
from io import BytesIO

import numpy as np
from flask import Flask, render_template, request
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from qiskit import QuantumCircuit

app = Flask(__name__)


def qft_rotations(circuit, n):
    """Performs qft on the first n qubits in circuit (without swaps)"""
    if n == 0:
        return circuit
    n -= 1
    circuit.h(n)
    for qubit in range(n):
        circuit.cp(np.pi / 2 ** (n - qubit), qubit, n)
    qft_rotations(circuit, n)


def swap_registers(circuit, n):
    for qubit in range(n // 2):
        circuit.swap(qubit, n - qubit - 1)
    return circuit


def qft(circuit, n):
    """QFT on the first n qubits in circuit"""
    qft_rotations(circuit, n)
    swap_registers(circuit, n)
    return circuit


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        try:
            num_qubits = int(request.form.get('num_qubits', 3))
            fig = Figure(figsize=(6, 4), dpi=400)
            canvas = FigureCanvas(fig)
            ax = fig.add_subplot(111)

            qc = QuantumCircuit(num_qubits)
            qft(qc, num_qubits)
            qc.draw(output="mpl", style="clifford", ax=ax)

            fig.tight_layout()

            output = BytesIO()
            canvas.print_png(output)
            output.seek(0)
            img_data = base64.b64encode(output.read()).decode('utf-8')

            qc_text = qc.draw(output="text")

            return render_template('index.html', img_data=img_data, qc_text=qc_text)
        except ValueError as ve:
            return str(ve), 400
        except Exception as e:
            return str(e), 500
    else:
        return render_template('index.html')


@app.route('/details')
def details():
    return render_template('details.html')


app.run(host='0.0.0.0', port=3000)