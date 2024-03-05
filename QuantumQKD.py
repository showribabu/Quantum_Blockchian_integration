from qiskit import QuantumCircuit, Aer, transpile, assemble, QuantumRegister, ClassicalRegister,execute


class Commander:
    def __init__(self, name, password):
        self.name = name
        self.password = password
        self.qubit = None
        self.shared_key = None
        self.messages = {}  # Store messages for simplicity

def create_bb84_circuit():
    qreg = QuantumRegister(2, name='q')
    creg = ClassicalRegister(2, name='c')
    circuit = QuantumCircuit(qreg, creg)

    circuit.h(qreg[0])
    circuit.x(qreg[1])
    
    # Add measurements
    circuit.measure(qreg, creg)

    return circuit


def establish_key(sender, receiver, backend):
    # Sender creates qubit
    sender.qubit = create_bb84_circuit()
    print('Sender circuit',sender.qubit)

    # Receiver measures qubit
    receiver.qubit = create_bb84_circuit()
    print('receiver circuit',receiver.qubit)
    
    receiver.qubit.measure(receiver.qubit.qregs[0], receiver.qubit.cregs[0])
    
   # Transpile the circuits
    transpiled_sender = transpile(sender.qubit, backend)
    transpiled_receiver = transpile(receiver.qubit, backend)
    
    print(transpiled_sender,transpiled_receiver)
    
    # Simulate the quantum communication
    result_sender = execute_and_get_result(transpiled_sender, backend)
    result_receiver = execute_and_get_result(transpiled_receiver, backend)
    print("Sender Job Status:", result_sender.status)
    print("Receiver Job Status:", result_receiver.status)
    
    print(result_sender ,'Type is' , type(result_sender))
    print(result_receiver ,'Type is' , type(result_receiver))
    # counts_sender = result_sender.get_counts(0) 
    # counts_receiver = result_receiver.get_counts(0)
    counts_sender = result_sender.results[0].data.counts
    counts_receiver = result_receiver.results[0].data.counts
    print(counts_receiver,counts_sender)

    # Extract key from matching results
    key_sender = extract_key(result_sender)
    key_receiver = extract_key(result_receiver)

    # Compare and establish a shared secret key
    shared_key = compare_and_extract_shared_key(key_sender, key_receiver)

    # Store the shared key for authentication
    receiver.shared_key = shared_key
    print('Shared key is ',receiver.shared_key)



def execute_and_get_result(circuit, backend):
    # Execute the circuit
    job = execute(circuit, backend)

    # Get the result
    result = job.result()

    # Return the result object
    return result


def extract_key(result):
    counts = result.get_counts()
    return list(counts.keys())[0]


def compare_and_extract_shared_key(key_a, key_b):
    shared_key = ""
    for bit_a, bit_b in zip(key_a, key_b):
        if bit_a == bit_b:
            shared_key += bit_a
    return shared_key


def generate_shared_key(admin, commanders):
    shared_keys = {}

    # Simulate the quantum communication
    simulator = Aer.get_backend('qasm_simulator')

    # Admin establishes keys with commanders
    for commander in commanders:
        establish_key(admin, commander, simulator)
        shared_keys[commander.name] = commander.shared_key

    return shared_keys

if __name__ == "__main__":
    admin = Commander("Admin", "admin_password")
    commander1 = Commander("Commander1", "commander1_password")
    commander2 = Commander("Commander2", "commander2_password")
    
    commanders_list = [commander1, commander2]
    
    shared_keys = generate_shared_key(admin, commanders_list)
    
    print("Shared Keys:", shared_keys)
