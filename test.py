from qiskit import QuantumCircuit, Aer, transpile, assemble, QuantumRegister, ClassicalRegister
from qiskit.visualization import plot_histogram
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import base64
from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit, transpile, Aer, execute

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


def authenticate_commander(admin, commander):
    # Commanders authenticate with the stored shared key and password
    if admin.password == commander.password and commander.shared_key is not None:
        print(f"{commander.name} is authenticated.")
        return True
    else:
        print(f"{commander.name} failed authentication.")
        return False

def send_message(sender, receiver, message):
    if authenticate_commander(sender, receiver):
        encrypted_message = encrypt_message(message, receiver.shared_key)
        receiver.messages[sender.name] = encrypted_message
        print(f"Message sent from {sender.name} to {receiver.name}: {message}")

def receive_message(receiver, sender):
    if authenticate_commander(receiver, sender):
        encrypted_message = receiver.messages.get(sender.name, None)
        if encrypted_message:
            decrypted_message = decrypt_message(encrypted_message, receiver.shared_key)
            print(f"Message received by {receiver.name} from {sender.name}: {decrypted_message}")
        else:
            print(f"No message from {sender.name} to {receiver.name}")

def encrypt_message(message, key):
    # Use AES-GCM for encryption
    cipher = Cipher(algorithms.AES(key), modes.GCM(b'\x00' * 12), backend=default_backend())
    encryptor = cipher.encryptor()

    # Pad the message
    padder = padding.PKCS7(128).padder()
    padded_message = padder.update(message.encode()) + padder.finalize()

    # Encrypt and get the tag
    ciphertext = encryptor.update(padded_message) + encryptor.finalize()
    tag = encryptor.tag

    # Combine ciphertext and tag
    encrypted_message = base64.b64encode(ciphertext + tag).decode()
    return encrypted_message

def decrypt_message(encrypted_message, key):
    # Use AES-GCM for decryption
    cipher = Cipher(algorithms.AES(key), modes.GCM(b'\x00' * 12), backend=default_backend())

    # Decode the base64 encoded message
    decoded_message = base64.b64decode(encrypted_message)

    # Split ciphertext and tag
    ciphertext, tag = decoded_message[:-16], decoded_message[-16:]

    # Decrypt the message
    decryptor = cipher.decryptor()
    decrypted_message = decryptor.update(ciphertext) + decryptor.finalize()

    # Unpad the message
    unpadder = padding.PKCS7(128).unpadder()
    original_message = unpadder.update(decrypted_message) + unpadder.finalize()

    return original_message.decode()

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

if __name__ == "__main__":
    admin = Commander("Admin", "admin_password")
    commander1 = Commander("Commander1", "commander1_password")
    commander2 = Commander("Commander2", "commander2_password")
    print(admin,commander1,commander2)
    

    # Simulate the quantum communication
    simulator = Aer.get_backend('qasm_simulator')
    
    print(simulator)
    

    # Admin establishes keys with commanders
    establish_key(admin, commander1, simulator)
    establish_key(admin, commander2, simulator)
    

    # Commanders send and receive messages
    send_message(commander1, commander2, "Hello Commander2!")
    send_message(commander2, commander1, "Greetings Commander1!")

    receive_message(commander2, commander1)
    receive_message(commander1, commander2)
