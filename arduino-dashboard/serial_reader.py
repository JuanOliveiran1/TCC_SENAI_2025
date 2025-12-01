# serial_reader.py
import threading
import time
import json
from collections import deque
import serial
import serial.tools.list_ports

class SerialReader:
    def __init__(self, port=None, baudrate=9600, buffer_size=200, reconnect_interval=3):
        self.port = port
        self.baudrate = baudrate
        self.buffer = deque(maxlen=buffer_size)  # armazena dicts com os dados
        self.events = deque(maxlen=200)          # armazena eventos tipo {"tipo":"EVENTO","msg":"..."}
        self._stop = threading.Event()
        self._thread = None
        self._ser = None
        self.reconnect_interval = reconnect_interval

    def list_ports(self):
        ports = serial.tools.list_ports.comports()
        return [p.device for p in ports]

    def start(self):
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=1)
        self._close_serial()

    def _open_serial(self):
        try:
            if not self.port:
                available = self.list_ports()
                if not available:
                    return False
                self.port = available[0]
            self._ser = serial.Serial(self.port, self.baudrate, timeout=1)
            return True
        except Exception as e:
            # não levantar exceção aqui, apenas retornar False
            self._ser = None
            return False

    def _close_serial(self):
        try:
            if self._ser and self._ser.is_open:
                self._ser.close()
        except:
            pass
        self._ser = None

    def _try_parse_line(self, line):
        line = line.strip()
        if not line:
            return None
        try:
            obj = json.loads(line)
            return obj
        except json.JSONDecodeError:
            # Tenta limpar caracteres inválidos comuns
            try:
                # remover bytes não imprimíveis
                clean = ''.join(ch for ch in line if ord(ch) >= 32)
                obj = json.loads(clean)
                return obj
            except Exception:
                return None

    def _handle_obj(self, obj):
        # Se veio um evento {"tipo":"EVENTO","msg":"..."}
        if isinstance(obj, dict):
            if obj.get("tipo") == "EVENTO" and "msg" in obj:
                self.events.append({"ts": time.time(), "msg": obj.get("msg")})
            else:
                # normaliza / adicione timestamp se necessário
                obj.setdefault("ts", time.time())
                self.buffer.append(obj)

    def _run(self):
        while not self._stop.is_set():
            if not self._ser or not getattr(self._ser, "is_open", False):
                opened = self._open_serial()
                if not opened:
                    time.sleep(self.reconnect_interval)
                    continue

            try:
                # lê linha completa
                raw = self._ser.readline().decode('utf-8', errors='ignore')
                obj = self._try_parse_line(raw)
                if obj is None:
                    # ignora linha inválida
                    continue
                self._handle_obj(obj)
            except Exception:
                # em caso de erro, tenta fechar e reconectar
                self._close_serial()
                time.sleep(self.reconnect_interval)

    # API para o app
    def get_latest(self):
        return list(self.buffer)[-1] if self.buffer else None

    def get_history(self, n=100):
        return list(self.buffer)[-n:]

    def get_events(self, n=50):
        return list(self.events)[-n:]
