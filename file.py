import customtkinter as ctk
import threading
import time
import csv,re
import pyvisa
from optosigma import GSC01

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ScanApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("OptoSigma Stage & Scope Controller")
        self.geometry("900x750")
        
        self.stage = None
        self.scope = None
        self.rm = pyvisa.ResourceManager()

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0) 

        self.create_connection_frame()
        self.create_motion_frame()
        self.create_scan_params_frame()
        self.create_log_frame()
        self.create_action_buttons()

        self.refresh_scope_ports()

    def create_connection_frame(self):
        self.frame_conn = ctk.CTkFrame(self)
        self.frame_conn.grid(row=0, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        
        self.lbl_conn = ctk.CTkLabel(self.frame_conn, text="Hardware Connections", font=("Roboto", 16, "bold"))
        self.lbl_conn.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.lbl_stage = ctk.CTkLabel(self.frame_conn, text="Stage Port:")
        self.lbl_stage.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.entry_stage_port = ctk.CTkEntry(self.frame_conn, placeholder_text="/dev/ttyUSB0")
        self.entry_stage_port.insert(0, "/dev/ttyUSB0")
        self.entry_stage_port.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        self.lbl_scope = ctk.CTkLabel(self.frame_conn, text="Oscilloscope (VISA):")
        self.lbl_scope.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.combo_scope_port = ctk.CTkComboBox(self.frame_conn, values=["Scanning..."])
        self.combo_scope_port.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        
        self.btn_refresh = ctk.CTkButton(self.frame_conn, text="Refresh", width=80, command=self.refresh_scope_ports)
        self.btn_refresh.grid(row=2, column=2, padx=10, pady=5)

        self.btn_connect = ctk.CTkButton(self.frame_conn, text="Connect All", fg_color="green", command=self.connect_hardware)
        self.btn_connect.grid(row=3, column=0, columnspan=3, padx=10, pady=15, sticky="ew")

    def create_motion_frame(self):
        self.frame_motion = ctk.CTkFrame(self)
        self.frame_motion.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        self.lbl_motion = ctk.CTkLabel(self.frame_motion, text="Motion Control", font=("Roboto", 16, "bold"))
        self.lbl_motion.grid(row=0, column=0, columnspan=2, padx=10, pady=5)

        self.btn_set_zero = ctk.CTkButton(self.frame_motion, text="Set Current as Zero (R:)", command=self.set_origin)
        self.btn_set_zero.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.btn_go_zero = ctk.CTkButton(self.frame_motion, text="Return to Origin", command=self.return_to_origin)
        self.btn_go_zero.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        self.lbl_speed = ctk.CTkLabel(self.frame_motion, text="Speed (mm/s):")
        self.lbl_speed.grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.entry_speed = ctk.CTkEntry(self.frame_motion)
        self.entry_speed.insert(0, "25")
        self.entry_speed.grid(row=2, column=1, padx=10, pady=5, sticky="w")

    def create_scan_params_frame(self):
        self.frame_params = ctk.CTkFrame(self)
        self.frame_params.grid(row=1, column=1, padx=20, pady=10, sticky="nsew")

        self.lbl_params = ctk.CTkLabel(self.frame_params, text="Scan Parameters", font=("Roboto", 16, "bold"))
        self.lbl_params.grid(row=0, column=0, columnspan=2, padx=10, pady=5)

        self.lbl_dist = ctk.CTkLabel(self.frame_params, text="Total Distance (mm):")
        self.lbl_dist.grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.entry_dist = ctk.CTkEntry(self.frame_params)
        self.entry_dist.insert(0, "20")
        self.entry_dist.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        self.lbl_step = ctk.CTkLabel(self.frame_params, text="Step Size (mm):")
        self.lbl_step.grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.entry_step = ctk.CTkEntry(self.frame_params)
        self.entry_step.insert(0, "2")
        self.entry_step.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        self.lbl_measure = ctk.CTkLabel(self.frame_params, text="Measurements/Step:")
        self.lbl_measure.grid(row=3, column=0, padx=10, pady=5, sticky="e")
        self.entry_measure = ctk.CTkEntry(self.frame_params)
        self.entry_measure.insert(0, "3")
        self.entry_measure.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        self.lbl_delay = ctk.CTkLabel(self.frame_params, text="Delay (s):")
        self.lbl_delay.grid(row=4, column=0, padx=10, pady=5, sticky="e")
        self.entry_delay = ctk.CTkEntry(self.frame_params)
        self.entry_delay.insert(0, "0.5")
        self.entry_delay.grid(row=4, column=1, padx=10, pady=5, sticky="w")

        self.chk_return = ctk.CTkCheckBox(self.frame_params, text="Measure on Return?")
        self.chk_return.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

    def create_log_frame(self):
        self.txt_log = ctk.CTkTextbox(self, height=150)
        self.txt_log.grid(row=2, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")
        self.log("System Ready. Please connect hardware.")

    def create_action_buttons(self):
        self.btn_start = ctk.CTkButton(self, text="START SCAN", height=50, font=("Roboto", 18, "bold"), fg_color="#E91E63", hover_color="#C2185B", command=self.start_scan_thread)
        self.btn_start.grid(row=3, column=0, columnspan=2, padx=20, pady=20, sticky="ew")

    def log(self, message):
        self.txt_log.insert("end", message + "\n")
        self.txt_log.see("end")

    def refresh_scope_ports(self):
        try:
            resources = self.rm.list_resources()
            usb_resources = [r for r in resources if 'USB' in r]
            if usb_resources:
                self.combo_scope_port.configure(values=usb_resources)
                self.combo_scope_port.set(usb_resources[0])
            else:
                self.combo_scope_port.configure(values=["No USB Scope Found"])
                self.log("No USB Oscilloscope found via VISA.")
        except Exception as e:
            self.log(f"Error listing ports: {e}")

    def connect_hardware(self):
        stage_port = self.entry_stage_port.get()
        scope_port = self.combo_scope_port.get()

        try:
            self.stage = GSC01(stage_port)
            self.log(f"Stage connected on {stage_port}")
        except Exception as e:
            self.log(f"Failed to connect Stage: {e}")
            return

        try:
            if "No USB" not in scope_port:
                self.scope = self.rm.open_resource(scope_port)
                self.scope.timeout = 5000
                self.scope.clear()
                idn = self.scope.query('*IDN?').strip()
                self.log(f"Scope connected: {idn}")
            else:
                self.log("Scope connection skipped (invalid port).")
        except Exception as e:
            self.log(f"Failed to connect Scope: {e}")

    def set_origin(self):
        if self.stage:
            try:
                self.stage.set_logical_zero()
                self.log("Current position set as Logical Zero (0).")
            except Exception as e:
                self.log(f"Error setting zero: {e}")

    def return_to_origin(self):
        if self.stage:
            try:
                self.log("Returning to origin...")
                self.stage.return_origin()
                self.log("At Origin.")
            except Exception as e:
                self.log(f"Error returning to origin: {e}")

    def definir_velocidade(self, mm_s, resolucao_mm=0.002):
        vmax = int(mm_s / resolucao_mm)
        vmin = int(vmax * 0.1)
        self.stage.set_speed(vmin, vmax, 200)

    def mover_relativo(self, dist_mm, resolucao_mm=0.002):
        pulsos = int(dist_mm / resolucao_mm)
        self.stage.position += pulsos
        self.stage.sleep_until_stop()

    def _get_scaling_val(self, channel, param):
        """
        Lê parâmetros de escala do bloco WAVEDESC via comando INSPECT.
        Trata a resposta mostrada no manual: C1:INSP "VERTICAL_GAIN: 1.2207e-005"
        """
        try:
            # Envia: C1:INSPECT? "VERTICAL_GAIN"
            query_str = f'{channel}:INSPECT? "{param}"'
            response = self.scope.query(query_str).strip()
            
            # A resposta vem suja, ex: 'C1:INSP "VERTICAL_GAIN: 1.2207e-005"'
            # Vamos usar Regex para extrair o número científico (ex: 1.22e-05)
            # Procura por número flutuante (positivo ou negativo) no final da string
            match = re.search(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', response.split(':')[-1])
            
            if match:
                val = float(match.group())
                return val
            else:
                self.log(f"Aviso: Não consegui extrair número de '{response}'. Usando 1.0")
                return 1.0
                
        except Exception as e:
            self.log(f"Erro lendo {param} em {channel}: {e}")
            return 1.0
    def capturar_dados(self, step_identifier, n_medicoes, delay):
        """
        Captura dados de C1 e C2, converte de Binário para Volts/Segundos
        e salva em CSV legível.
        """
        
        # 1. Configuração Inicial para Leitura
        try:
            # Parar aquisição para garantir sincronia entre canais
            self.scope.write(r"""vbs 'app.acquisition.triggermode = "stopped" ' """)
            self.scope.query(r"""vbs? 'return=app.WaitUntilIdle(5)' """)
            
            # Configuração OBRIGATÓRIA para LeCroy (Binário, 16-bit Word)
            self.scope.write("COMM_HEADER OFF")
            self.scope.write("CORD LO")
            self.scope.write("COMM_FORMAT DEF9, WORD, BIN")
        except Exception as e:
            self.log(f"Erro na configuração inicial: {e}")
            return

        for m in range(n_medicoes):
            self.log(f"Iniciando medição {m+1} de {n_medicoes}...")
            
            # Dispara uma aquisição única (Single) se necessário, ou apenas lê o que está na tela
            # Se o scope já estiver parado com uma onda na tela, pule esta linha.
            # Se precisar capturar algo novo a cada loop:
            self.scope.write(r"""vbs 'app.acquisition.triggermode = "single" ' """)
            self.scope.query(r"""vbs? 'return=app.WaitUntilIdle(5)' """)

            for k in range(1, 3): # Canais 1 e 2
                channel = f"C{k}"
                filename = f"{step_identifier}_meas_{m}_channel_{k}.csv"
                
                try:
                    # A. Ler Fatores de Escala (Necessário para converter Binário -> Volts)
                    v_gain = self._get_scaling_val(channel, "VERTICAL_GAIN")
                    v_offset = self._get_scaling_val(channel, "VERTICAL_OFFSET")
                    h_interval = self._get_scaling_val(channel, "HORIZ_INTERVAL")
                    h_offset = self._get_scaling_val(channel, "HORIZ_OFFSET")

                    # B. Ler Dados Binários
                    # datatype='h' informa ao PyVISA que são "short integers" (16-bit), como definido por "WORD"
                    raw_data = self.scope.query_binary_values(
                        f"{channel}:WF? DAT1", 
                        datatype='h', 
                        is_big_endian=False, 
                        container=list
                    )

                    # C. Converter e Salvar em CSV
                    with open(filename, "w", newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow(['Index', 'Tempo (s)', 'Amplitude (V)'])
                        
                        for i, raw_val in enumerate(raw_data):
                            # Matemática de conversão
                            tempo = (i * h_interval) + h_offset
                            volts = (raw_val * v_gain) - v_offset
                            
                            writer.writerow([i, f"{tempo:.8e}", f"{volts:.6f}"])
                    
                    self.log(f"Arquivo salvo: {filename} ({len(raw_data)} pontos)")

                except Exception as e:
                    self.log(f"Erro capturando {channel} na medição {m}: {e}")

            # Aguarda antes da próxima medição
            time.sleep(delay)

        # Retorna o osciloscópio para modo normal ao final de tudo
        try:
            self.scope.write(r"""vbs 'app.acquisition.triggermode = "auto" ' """)
        except:
            pass

    def start_scan_thread(self):
        if not self.stage or not self.scope:
            self.log("Error: Hardware not connected.")
            return
        t = threading.Thread(target=self.run_scan_logic)
        t.start()

    def run_scan_logic(self):
        self.btn_start.configure(state="disabled", text="SCANNING...")
        try:
            dist_total = float(self.entry_dist.get())
            step_mm = float(self.entry_step.get())
            n_measure = int(self.entry_measure.get())
            delay = float(self.entry_delay.get())
            measure_return = bool(self.chk_return.get())
            speed = float(self.entry_speed.get())

            self.definir_velocidade(speed)
            
            num_steps = int(dist_total / step_mm)
            self.log(f"--- Starting Scan: {dist_total}mm, {num_steps} steps ---")

            for i in range(num_steps):
                self.mover_relativo(step_mm)
                self.log(f"[FORWARD] Step {i+1}/{num_steps} reached. Measuring...")
                self.capturar_dados("forward-"+str(i), n_measure, delay)

            if measure_return:
                self.log("--- Starting Backward Scan ---")
                for i in range(num_steps):
                    self.mover_relativo(-step_mm)
                    self.log(f"[BACKWARD] Step {i+1}/{num_steps} reached. Measuring...")
                    idx_back = 'backward-'+str(i) 
                    self.capturar_dados(idx_back, n_measure, delay)
            else:
                self.log("--- Returning to Start ---")
                self.mover_relativo(-dist_total)
            
            self.log("--- Scan Complete ---")

        except Exception as e:
            self.log(f"Critical Scan Error: {e}")
        finally:
            self.scope.close()
            self.btn_start.configure(state="normal", text="START SCAN")

if __name__ == "__main__":
    app = ScanApp()
    app.mainloop()
