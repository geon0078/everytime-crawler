"""
에브리타임 대량 크롤링 GUI 도구
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import queue
import subprocess
from datetime import datetime


class MassiveCrawlingGUI:
    """대량 크롤링 GUI 클래스"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("에브리타임 대량 게시판 크롤링")
        self.root.geometry("800x600")
        
        # 큐를 통한 스레드 간 통신
        self.output_queue = queue.Queue()
        self.crawling_thread = None
        self.is_crawling = False
        
        self.setup_ui()
        self.check_environment()
        
        # 주기적으로 큐 확인
        self.root.after(100, self.check_output_queue)
    
    def setup_ui(self):
        """UI 구성"""
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 제목
        title_label = ttk.Label(main_frame, text="에브리타임 대량 게시판 크롤링", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # 설정 프레임
        config_frame = ttk.LabelFrame(main_frame, text="크롤링 설정", padding="10")
        config_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 게시판 선택
        ttk.Label(config_frame, text="대상 게시판:").grid(row=0, column=0, sticky=tk.W)
        self.board_var = tk.StringVar(value="all")
        
        board_frame = ttk.Frame(config_frame)
        board_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
        
        ttk.Radiobutton(board_frame, text="모든 게시판", variable=self.board_var, 
                       value="all").grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(board_frame, text="주요 게시판만", variable=self.board_var, 
                       value="major").grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # 페이지 수 설정
        ttk.Label(config_frame, text="게시판당 최대 페이지:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.max_pages_var = tk.StringVar(value="500")
        pages_spinbox = ttk.Spinbox(config_frame, from_=1, to=1000, width=10, 
                                   textvariable=self.max_pages_var)
        pages_spinbox.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=(10, 0))
        
        # 대기 시간 설정
        ttk.Label(config_frame, text="페이지 간 대기시간(초):").grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        self.delay_var = tk.StringVar(value="3")
        delay_spinbox = ttk.Spinbox(config_frame, from_=1, to=10, width=10, 
                                   textvariable=self.delay_var)
        delay_spinbox.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=(10, 0))
        
        # 저장 경로
        ttk.Label(config_frame, text="저장 경로:").grid(row=3, column=0, sticky=tk.W, pady=(10, 0))
        path_frame = ttk.Frame(config_frame)
        path_frame.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(10, 0))
        
        self.save_path_var = tk.StringVar(value="data")
        path_entry = ttk.Entry(path_frame, textvariable=self.save_path_var, width=30)
        path_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        path_button = ttk.Button(path_frame, text="찾기", command=self.browse_save_path)
        path_button.grid(row=0, column=1, padx=(5, 0))
        
        # 컨트롤 버튼
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0))
        
        self.start_button = ttk.Button(button_frame, text="크롤링 시작", 
                                      command=self.start_crawling, style="Accent.TButton")
        self.start_button.grid(row=0, column=0, padx=(0, 5))
        
        self.stop_button = ttk.Button(button_frame, text="중단", 
                                     command=self.stop_crawling, state="disabled")
        self.stop_button.grid(row=0, column=1, padx=(5, 0))
        
        self.analyze_button = ttk.Button(button_frame, text="데이터 분석", 
                                        command=self.analyze_data)
        self.analyze_button.grid(row=0, column=2, padx=(10, 0))
        
        # 진행률 표시
        progress_frame = ttk.LabelFrame(main_frame, text="진행 상황", padding="10")
        progress_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.progress_var = tk.StringVar(value="대기 중...")
        progress_label = ttk.Label(progress_frame, textvariable=self.progress_var)
        progress_label.grid(row=0, column=0, sticky=tk.W)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # 출력 로그
        log_frame = ttk.LabelFrame(main_frame, text="크롤링 로그", padding="10")
        log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 그리드 가중치 설정
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        config_frame.columnconfigure(1, weight=1)
        path_frame.columnconfigure(0, weight=1)
        progress_frame.columnconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
    
    def check_environment(self):
        """환경 확인"""
        self.log_message("🔍 환경 확인 중...")
        
        # .env 파일 확인
        if not os.path.exists('.env'):
            self.log_message("⚠️ .env 파일이 없습니다. 계정 정보를 설정해주세요.")
            messagebox.showwarning("환경 설정", ".env 파일이 없습니다.\n.env.example을 참고하여 계정 정보를 설정해주세요.")
        else:
            self.log_message("✅ .env 파일 확인됨")
        
        # 데이터 디렉토리 확인
        data_dir = self.save_path_var.get()
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            self.log_message(f"📁 데이터 디렉토리 생성: {data_dir}")
        else:
            self.log_message(f"📁 데이터 디렉토리 확인: {data_dir}")
    
    def browse_save_path(self):
        """저장 경로 선택"""
        path = filedialog.askdirectory(initialdir=self.save_path_var.get())
        if path:
            self.save_path_var.set(path)
    
    def log_message(self, message):
        """로그 메시지 추가"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, formatted_message)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def start_crawling(self):
        """크롤링 시작"""
        if self.is_crawling:
            return
        
        # 환경 확인
        if not os.path.exists('.env'):
            messagebox.showerror("오류", ".env 파일이 없습니다.")
            return
        
        # UI 상태 변경
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.progress_var.set("크롤링 시작 중...")
        self.progress_bar.start()
        self.is_crawling = True
        
        # 설정 수집
        config = {
            'board_type': self.board_var.get(),
            'max_pages': int(self.max_pages_var.get()),
            'delay': int(self.delay_var.get()),
            'save_path': self.save_path_var.get()
        }
        
        # 크롤링 스레드 시작
        self.crawling_thread = threading.Thread(target=self.run_crawling, args=(config,))
        self.crawling_thread.daemon = True
        self.crawling_thread.start()
        
        self.log_message("🚀 대량 크롤링 시작!")
    
    def run_crawling(self, config):
        """크롤링 실행 (별도 스레드)"""
        try:
            # 파이썬 스크립트 실행
            script_path = os.path.join("examples", "massive_board_crawling.py")
            
            # 환경변수 설정
            env = os.environ.copy()
            env['CRAWLING_GUI_MODE'] = '1'
            env['MAX_PAGES'] = str(config['max_pages'])
            env['DELAY'] = str(config['delay'])
            env['SAVE_PATH'] = config['save_path']
            
            if config['board_type'] == 'major':
                env['TARGET_BOARDS'] = 'free,secret,job,exam'
            
            # 프로세스 실행
            process = subprocess.Popen([
                sys.executable, script_path
            ], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            universal_newlines=True,
            env=env,
            bufsize=1)
            
            # 출력 읽기
            while True:
                if not self.is_crawling:
                    process.terminate()
                    break
                
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                
                if output:
                    self.output_queue.put(('output', output.strip()))
            
            # 프로세스 완료 처리
            return_code = process.wait()
            
            if return_code == 0:
                self.output_queue.put(('complete', '✅ 크롤링이 완료되었습니다!'))
            else:
                self.output_queue.put(('error', f'❌ 크롤링이 실패했습니다. (코드: {return_code})'))
                
        except Exception as e:
            self.output_queue.put(('error', f'❌ 크롤링 중 오류: {e}'))
    
    def stop_crawling(self):
        """크롤링 중단"""
        self.is_crawling = False
        self.progress_var.set("중단 중...")
        self.log_message("🛑 크롤링 중단 요청")
        
        # UI 상태 복원
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.progress_bar.stop()
        self.progress_var.set("중단됨")
    
    def analyze_data(self):
        """데이터 분석 실행"""
        self.log_message("📊 데이터 분석 시작...")
        
        try:
            script_path = os.path.join("examples", "analyze_massive_data.py")
            subprocess.Popen([sys.executable, script_path])
            self.log_message("📊 데이터 분석 도구가 실행되었습니다.")
        except Exception as e:
            self.log_message(f"❌ 데이터 분석 실행 실패: {e}")
            messagebox.showerror("오류", f"데이터 분석 실행 실패:\n{e}")
    
    def check_output_queue(self):
        """출력 큐 확인 및 처리"""
        try:
            while True:
                msg_type, message = self.output_queue.get_nowait()
                
                if msg_type == 'output':
                    self.log_message(message)
                elif msg_type == 'complete':
                    self.log_message(message)
                    self.stop_crawling()
                    messagebox.showinfo("완료", "크롤링이 완료되었습니다!")
                elif msg_type == 'error':
                    self.log_message(message)
                    self.stop_crawling()
                    messagebox.showerror("오류", message)
                    
        except queue.Empty:
            pass
        
        # 다시 예약
        self.root.after(100, self.check_output_queue)


def main():
    """메인 실행 함수"""
    try:
        root = tk.Tk()
        app = MassiveCrawlingGUI(root)
        root.mainloop()
    except ImportError as e:
        print(f"❌ tkinter를 사용할 수 없습니다: {e}")
        print("명령줄에서 massive_board_crawling.py를 직접 실행하세요.")
    except Exception as e:
        print(f"❌ GUI 실행 중 오류: {e}")


if __name__ == "__main__":
    main()
