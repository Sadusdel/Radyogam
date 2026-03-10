import pandas as pd
import customtkinter as ctk
from tkinter import messagebox, ttk
import os
import re

# --- Görünüm Ayarları ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class DentalAIApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("ORAL DIAGNOZ AI | Klinik Karar Destek Sistemi")
        self.geometry("1400x900")
        
        # --- Veri Kaynakları ---
        self.csv_files = [
            "Yumusak_Doku_Kistler.csv", "Odontojenik_Kistler.csv", "Non-Odontojen_Kistler.csv",
            "Benign_Odontojenik_Tumorler.csv", "Malign_Tumorler.csv", "Hematolojik_Maligniteler.csv",
            "Periapikal_Enfeksiyonlar.csv", "Cenede_Enfeksiyonlar.csv", "Endokrin_Bozukluklar.csv",
            "Metabolik_Kemik.csv", "Sistemik_Bozukluklar.csv", "Distrofik_Kalsifikasyon.csv",
            "Idiyopatik_Kalsifikasyon.csv", "Diger_Kalsifikasyon.csv", "Beyaz Lezyonlar.csv",
            "Kırmızı Lezyonlar.csv", "Oral Pigmentasyonlar.csv", "Non-Odontojen_Agri.csv"
        ]
        
        self.full_data = self.load_all_data()
        self.setup_ui()

    def load_all_data(self):
        all_dfs = []
        for file in self.csv_files:
            if os.path.exists(file):
                try:
                    try:
                        df = pd.read_csv(file, encoding='utf-8')
                    except:
                        df = pd.read_csv(file, encoding='latin-1')
                    df.columns = [c.strip() for c in df.columns]
                    df['Kaynak_Dosya'] = file.replace('.csv', '').replace('_', ' ')
                    df = df[df['Tanı Adı'].notna()]
                    all_dfs.append(df)
                except Exception as e:
                    print(f"Hata: {file} yüklenemedi. {e}")
        return pd.concat(all_dfs, ignore_index=True) if all_dfs else pd.DataFrame()

    def setup_ui(self):
        self.tabs = ctk.CTkTabview(self, segmented_button_selected_color="#1f538d")
        self.tabs.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab_library = self.tabs.add("📚 Tanı Kütüphanesi")
        self.tab_analysis = self.tabs.add("🔬 Klinik Vaka Analizi")

        self.setup_library_tab()
        self.setup_analysis_tab()

    def setup_library_tab(self):
        self.sidebar = ctk.CTkFrame(self.tab_library, width=300, corner_radius=10)
        self.sidebar.pack(side="left", fill="y", padx=10, pady=10)
        
        ctk.CTkLabel(self.sidebar, text="🔍 FİLTRELEME", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20, padx=20)
        
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self.update_list)
        ctk.CTkLabel(self.sidebar, text="Belirti veya Tanı Ara:").pack(anchor="w", padx=20)
        self.search_entry = ctk.CTkEntry(self.sidebar, placeholder_text="Örn: Sabun köpüğü...", textvariable=self.search_var, width=260)
        self.search_entry.pack(pady=(5, 20), padx=20)

        ctk.CTkLabel(self.sidebar, text="Lezyon Kategorisi:").pack(anchor="w", padx=20)
        categories = ["Tümü"] + sorted(list(self.full_data['Kaynak_Dosya'].unique())) if not self.full_data.empty else ["Tümü"]
        self.cat_filter = ctk.CTkOptionMenu(self.sidebar, values=categories, command=self.update_list, width=260)
        self.cat_filter.pack(pady=(5, 20), padx=20)

        self.lib_content = ctk.CTkFrame(self.tab_library, fg_color="transparent")
        self.lib_content.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.scroll_canvas = ctk.CTkScrollableFrame(self.lib_content, label_text="Tüm Kayıtlar")
        self.scroll_canvas.pack(fill="both", expand=True)

        self.stats_label = ctk.CTkLabel(self.sidebar, text="Yükleniyor...", font=("Arial", 11, "italic"))
        self.stats_label.pack(side="bottom", pady=20)
        self.update_list()

    def setup_analysis_tab(self):
        container = ctk.CTkScrollableFrame(self.tab_analysis)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(container, text="KLİNİK VAKA ANALİZİ", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(10, 20))
        
        # --- Temel Bilgiler Paneli ---
        base_info_frame = ctk.CTkFrame(container)
        base_info_frame.pack(fill="x", padx=40, pady=10)
        
        fields = [
            ("Yaş Aralığı:", ["0-10", "10-20", "20-30", "30-50", "50+"]),
            ("Cinsiyet:", ["K", "E", "Fark etmez"]),
            ("Lokalizasyon:", ["Mandibula Posterior", "Mandibula Anterior", "Maksilla Posterior", "Maksilla Anterior", "Yumuşak Doku", "Sinüs / Antrum"])
        ]

        self.analysis_inputs = {}
        for label_text, options in fields:
            row = ctk.CTkFrame(base_info_frame, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=8)
            ctk.CTkLabel(row, text=label_text, width=140, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left")
            var = ctk.CTkOptionMenu(row, values=options, width=300)
            var.pack(side="left", padx=10)
            self.analysis_inputs[label_text] = var

        # --- WHO STANDARTLARINA GÖRE RADYOLOJİK GÖRÜNÜM ---
        rad_main_frame = ctk.CTkFrame(container)
        rad_main_frame.pack(fill="x", padx=40, pady=15)
        
        ctk.CTkLabel(rad_main_frame, text="☢️ RADYOGRAFİK PARAMETRELER (WHO STANDARTLARI)", 
                     font=ctk.CTkFont(size=15, weight="bold"), text_color="#3a7ebf").pack(pady=10)

        # Kategorize edilmiş opsiyonlar
        rad_categories = {
            "1. Sınır ve Kenar Yapısı": [
                "Keskin Sınırlı (Kortike)", 
                "Sklerotik Kenar", 
                "Düzensiz/İnvaziv Kenar", 
                "Yumrukla Delinmiş (Punched-out)",
                "İnce Ekspansiyonlu Kenar"
            ],
            "2. İç Yapı ve Dansite": [
                "Radyolüsent (Tam)", 
                "Radyoopak (Tam)", 
                "Mikst (Lüsent+Opak)", 
                "Multiloküler (Sabun Köpüğü)", 
                "Multiloküler (Bal Peteği)",
                "Mat Buz Camı (Ground Glass)",
                "Pamuk Atılmış Manzarası"
            ],
            "3. Çevre Dokularla İlişki": [
                "Kök Rezorbsiyonu", 
                "Gömülü Dişle İlişkili", 
                "Mandibüler Kanal İtilmesi", 
                "Periost Reaksiyonu (Soğan Kabuğu)", 
                "Spiküler (Güneş Işını)",
                "Lamina Dura Kaybı",
                "Kortikal Perforasyon"
            ]
        }

        self.rad_checks = {}
        
        grid_container = ctk.CTkFrame(rad_main_frame, fg_color="transparent")
        grid_container.pack(fill="x", padx=10, pady=5)

        for idx, (cat_name, opts) in enumerate(rad_categories.items()):
            cat_box = ctk.CTkFrame(grid_container, border_width=1, border_color="#444")
            cat_box.grid(row=0, column=idx, padx=5, pady=5, sticky="nsew")
            grid_container.columnconfigure(idx, weight=1)
            
            ctk.CTkLabel(cat_box, text=cat_name, font=ctk.CTkFont(size=12, weight="bold"), text_color="#aaa").pack(pady=5)
            
            for opt in opts:
                var = ctk.BooleanVar()
                cb = ctk.CTkCheckBox(cat_box, text=opt, variable=var, font=ctk.CTkFont(size=11), height=22)
                cb.pack(anchor="w", padx=10, pady=2)
                self.rad_checks[opt] = var

        # --- Semptom Girişi ---
        semptom_frame = ctk.CTkFrame(container)
        semptom_frame.pack(fill="x", padx=40, pady=10)
        
        ctk.CTkLabel(semptom_frame, text="📝 EK SEMPTOMLAR & KLİNİK NOTLAR", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(10, 0))
        self.symptom_entry = ctk.CTkEntry(semptom_frame, placeholder_text="Ağrısız şişlik, parestezi, pürulan akıntı, ekspansiyon vb.", height=40)
        self.symptom_entry.pack(fill="x", padx=20, pady=(5, 15))

        # Analiz Butonu
        self.btn_run = ctk.CTkButton(container, text="🔍 VAKAYI SİSTEMATİK ANALİZ ET", height=50, 
                                     font=ctk.CTkFont(size=16, weight="bold"), fg_color="#2c6e49", hover_color="#1e4a32",
                                     command=self.run_clinical_analysis)
        self.btn_run.pack(pady=20)

        # Sonuç Alanı
        self.analysis_results_frame = ctk.CTkFrame(container, fg_color="transparent")
        self.analysis_results_frame.pack(fill="both", expand=True, pady=10)

    def run_clinical_analysis(self):
        """OPTIMAL VAKA ANALİZ FORMÜLASYONU"""
        for widget in self.analysis_results_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.analysis_results_frame, text="Analiz ediliyor, lütfen bekleyin...", font=("Arial", 12, "italic")).pack()
        self.update()

        # Inputlar
        vaka_yas = self.analysis_inputs["Yaş Aralığı:"].get()
        vaka_cinsiyet = self.analysis_inputs["Cinsiyet:"].get()
        vaka_lok_str = self.analysis_inputs["Lokalizasyon:"].get()
        vaka_lok = vaka_lok_str.lower()
        vaka_semptom_input = self.symptom_entry.get()
        vaka_semptom = vaka_semptom_input.lower().split()
        secili_rad = [opt for opt, var in self.rad_checks.items() if var.get()]

        # FORMÜL KATSAYILARI (Weighting Factor)
        W_RAD = 10    # Her bir radyolojik eşleşme
        W_LOK = 8     # Lokalizasyon doğruluğu
        W_SYM = 6     # Semptom benzerliği
        W_AGE = 4     # Demografik yaş uyumu
        W_GEN = 2     # Demografik cinsiyet uyumu

        matches = []
        for _, row in self.full_data.iterrows():
            score = 0
            potential_max = 0
            puan_detaylari = [] # Neden bu yüzde çıktığını açıklamak için veri tutuyoruz

            # 1. Yaş Analizi
            if pd.notna(row.get('Görüldüğü Yaş Aralığı')):
                potential_max += W_AGE
                if vaka_yas in str(row['Görüldüğü Yaş Aralığı']):
                    score += W_AGE
                    puan_detaylari.append(f"✓ Yaş Uyumu (+{W_AGE} Puan): Vaka yaşı ({vaka_yas}), literatür verisiyle ({row['Görüldüğü Yaş Aralığı']}) örtüşüyor.")

            # 2. Cinsiyet Analizi
            if vaka_cinsiyet != "Fark etmez" and pd.notna(row.get('Cinsiyet')):
                potential_max += W_GEN
                if vaka_cinsiyet in str(row['Cinsiyet']) or "K=E" in str(row['Cinsiyet']):
                    score += W_GEN
                    puan_detaylari.append(f"✓ Cinsiyet Uyumu (+{W_GEN} Puan): {vaka_cinsiyet} cinsiyeti bu tanı için tipik veya nötrdür.")

            # 3. Lokalizasyon Analizi
            if pd.notna(row.get('Lokalizasyon')):
                potential_max += W_LOK
                row_lok = str(row['Lokalizasyon']).lower()
                if any(word in row_lok for word in vaka_lok.split()):
                    score += W_LOK
                    puan_detaylari.append(f"✓ Lokalizasyon Uyumu (+{W_LOK} Puan): Belirtilen bölge ({vaka_lok_str}), lezyonun yaygın görüldüğü yerler arasındadır.")

            # 4. Radyolojik Bulgular
            rad_context = (str(row.get('Radyolojik Görüntü Özellikleri', '')) + " " + 
                           str(row.get('Özel Benzetmesi', ''))).lower()
            
            potential_max += len(secili_rad) * W_RAD
            for opt in secili_rad:
                clean_opt = opt.lower()
                matched = False
                if "(" in clean_opt:
                    alias = clean_opt.split("(")[1].replace(")", "").strip()
                    main_term = clean_opt.split("(")[0].strip()
                    if alias in rad_context or main_term in rad_context:
                        matched = True
                elif clean_opt in rad_context:
                    matched = True
                
                if matched:
                    score += W_RAD
                    puan_detaylari.append(f"★ Kritik Radyolojik Bulgu (+{W_RAD} Puan): '{opt}' kriteri tanı verileriyle tam eşleşiyor.")

            # 5. Semptom Analizi
            if vaka_semptom:
                row_sym = str(row.get('Semptomları', '')).lower()
                potential_max += W_SYM
                found_syms = [s for s in vaka_semptom if len(s) > 2 and s in row_sym]
                if found_syms:
                    sub_score = int(W_SYM * (len(found_syms) / len(vaka_semptom)))
                    score += sub_score
                    puan_detaylari.append(f"✓ Semptomatik Benzerlik (+{sub_score} Puan): '{', '.join(found_syms)}' klinik belirtileri bu tanıyı destekliyor.")

            if score > 0:
                final_percentage = int((score / max(potential_max, 1)) * 100)
                # Satıra analiz gerekçesini de ekliyoruz
                row_with_details = row.copy()
                row_with_details['Analiz_Gerekcesi'] = "\n".join(puan_detaylari)
                matches.append((final_percentage, row_with_details))

        # UI Temizliği ve Sıralama
        for widget in self.analysis_results_frame.winfo_children(): widget.destroy()
        matches.sort(key=lambda x: x[0], reverse=True)

        if not matches:
            ctk.CTkLabel(self.analysis_results_frame, text="Kriterlere uygun bir vaka eşleşmesi saptanamadı.", text_color="orange").pack()
        else:
            for perc, row in matches[:15]:
                self.create_analysis_card(row, perc)

    def create_analysis_card(self, row, percentage):
        card = ctk.CTkFrame(self.analysis_results_frame)
        card.pack(fill="x", padx=40, pady=5)
        
        score_color = "#2c6e49" if percentage > 65 else "#b58d12" if percentage > 35 else "#8b2e2e"
        
        lbl_score = ctk.CTkLabel(card, text=f"%{percentage} Uyum", fg_color=score_color, 
                                 text_color="white", corner_radius=5, width=110, font=ctk.CTkFont(weight="bold"))
        lbl_score.pack(side="right", padx=15)

        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(side="left", fill="both", expand=True, padx=15, pady=10)

        ctk.CTkLabel(info, text=str(row['Tanı Adı']).upper(), font=("Arial", 14, "bold"), text_color="#3a7ebf").pack(anchor="w")
        ctk.CTkLabel(info, text=f"Kategori: {row['Kaynak_Dosya']}", font=("Arial", 10), text_color="gray").pack(anchor="w")
        
        ctk.CTkButton(card, text="ANALİZ RAPORU", width=120, command=lambda r=row: self.show_details(r)).pack(side="right", padx=10)

    def update_list(self, *args):
        for widget in self.scroll_canvas.winfo_children(): widget.destroy()
        query = self.search_var.get().lower()
        selected_cat = self.cat_filter.get()

        df = self.full_data.copy()
        if selected_cat != "Tümü": df = df[df['Kaynak_Dosya'] == selected_cat]
        if query:
            mask = df.apply(lambda row: row.astype(str).str.contains(query, case=False).any(), axis=1)
            df = df[mask]

        self.stats_label.configure(text=f"Kütüphane: {len(self.full_data)} | Filtre: {len(df)}")
        for _, row in df.iterrows():
            self.create_result_card(row)

    def create_result_card(self, row):
        card = ctk.CTkFrame(self.scroll_canvas)
        card.pack(fill="x", pady=4, padx=5)
        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(side="left", fill="both", expand=True, padx=15, pady=8)
        ctk.CTkLabel(info, text=str(row['Tanı Adı']).upper(), font=("Arial", 13, "bold"), text_color="#3a7ebf").pack(anchor="w")
        
        btn = ctk.CTkButton(card, text="İNCELE", width=100, command=lambda r=row: self.show_details(r))
        btn.pack(side="right", padx=10)

    def show_details(self, row):
        detail_win = ctk.CTkToplevel(self)
        detail_win.title(f"Tanı Detayı: {row['Tanı Adı']}")
        detail_win.geometry("900x900")
        detail_win.attributes("-topmost", True)

        txt = ctk.CTkTextbox(detail_win, font=("Segoe UI", 14), padx=30, pady=30)
        txt.pack(fill="both", expand=True)

        report = f"📋 KLİNİK TANI ANALİZ RAPORU\n"
        report += f"Tanı: {row['Tanı Adı'].upper()}\n"
        report += "═" * 60 + "\n\n"
        
        # --- ANALİZ GEREKÇESİ BÖLÜMÜ (Yeni Eklenen) ---
        if 'Analiz_Gerekcesi' in row and row['Analiz_Gerekcesi']:
            report += "🧐 NEDEN BU SONUÇ ÇIKTI? (ALGORİTMA GEREKÇESİ)\n"
            report += "─" * 40 + "\n"
            report += f"{row['Analiz_Gerekcesi']}\n\n"
            report += "═" * 60 + "\n\n"

        report += "📑 LİTERATÜR VERİLERİ VE KLİNİK ÖZELLİKLER\n"
        report += "─" * 40 + "\n"
        
        for col in row.index:
            if col not in ['Kaynak_Dosya', 'Analiz_Gerekcesi'] and pd.notna(row[col]) and str(row[col]).strip() != "":
                report += f"● {col.upper()}:\n{row[col]}\n\n"
        
        txt.insert("0.0", report)
        txt.configure(state="disabled")

if __name__ == "__main__":
    app = DentalAIApp()
    app.mainloop()