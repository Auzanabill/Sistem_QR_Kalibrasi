# Flowchart Sistem Manajemen Sertifikat Kalibrasi (Mermaid)

Berikut adalah kode Mermaid untuk seluruh modul flowchart sistem. Anda dapat menyalin kode di bawah ini dan menempelkannya ke [Mermaid Live Editor](https://mermaid.live/), file Markdown (seperti GitHub/GitLab README), atau aplikasi yang mendukung Mermaid (seperti Notion, Obsidian).

---

## 1. Flowchart Utama (Login & Dashboard)

```mermaid
flowchart TD
    Start([Mulai]) --> Akses[Akses Sistem<br>Browser / Scan QR]
    Akses --> CheckLogin{Sudah Login?}
    
    CheckLogin -- Ya --> RedDash[Redirect ke Dashboard]
    CheckLogin -- Tidak --> CheckQR{Akses via QR Scan?}
    
    CheckQR -- Ya --> SaveSession[Simpan instrument_id di session]
    SaveSession --> RedLoginNext[Redirect ke Login<br>dengan next URL]
    RedLoginNext --> ShowLogin[Tampilkan Halaman Login]
    
    CheckQR -- Tidak --> ShowLogin
    
    ShowLogin --> InputUser[/Masukkan Username & Password/]
    InputUser --> CheckBlocked{Akun Diblokir?}
    
    CheckBlocked -- Ya --> MsgBlocked[Tampilkan Pesan 'Akun Diblokir'<br>+ Catat Access Log]
    MsgBlocked --> End1([Selesai])
    
    CheckBlocked -- Tidak --> CheckCreds{Kredensial Valid?}
    
    CheckCreds -- Ya --> ResetAttempt[Reset failed_attempts = 0<br>Catat Access Log login_success]
    ResetAttempt --> CheckNext{Ada next URL?}
    
    CheckNext -- Ya --> RedScanResult[Redirect ke Scan Result]
    CheckNext -- Tidak --> RedDash2[Redirect ke Dashboard]
    RedScanResult --> RedDash2
    
    CheckCreds -- Tidak --> IncAttempt[Increment failed_attempts + 1]
    IncAttempt --> CheckLimit{failed_attempts >= 3?}
    
    CheckLimit -- Ya --> BlockAccount[BLOKIR AKUN<br>is_blocked = True<br>Catat Access Log]
    BlockAccount --> End2([Selesai])
    
    CheckLimit -- Tidak --> ShowLeftMsg[Tampilkan Pesan 'Sisa Percobaan'<br>Catat Access Log]
    ShowLeftMsg --> BackLogin[Kembali ke Form Login]
    
    RedDash2 --> ShowDash[Tampilkan Dashboard]
    ShowDash --> End3([Selesai])
```

---

## 2. Flowchart Registrasi

```mermaid
flowchart TD
    Start([Mulai]) --> AksesReg[Akses Halaman Registrasi]
    AksesReg --> CheckLogin{Sudah Login?}
    
    CheckLogin -- Ya --> RedDash[Redirect ke Dashboard]
    
    CheckLogin -- Tidak --> ShowForm[/Tampilkan Form Registrasi/]
    ShowForm --> SubmitForm[Isi Form & Submit]
    SubmitForm --> CheckValid{Form Valid?}
    
    CheckValid -- Tidak --> ShowErr[Tampilkan Pesan Error Validasi]
    ShowErr --> ShowForm
    
    CheckValid -- Ya --> CreateUser[Buat User baru Django Auth]
    CreateUser --> CreateProfile[Buat UserProfile role=scanner]
    CreateProfile --> AutoLogin[Auto Login + Pesan Sukses]
    AutoLogin --> RedDash2[Redirect ke Dashboard]
    
    RedDash --> End([Selesai])
    RedDash2 --> End
```

---

## 3. Flowchart Scan QR Code

```mermaid
flowchart TD
    Start([Mulai]) --> ScanQR[Scan QR Code pada Instrumen Fisik]
    ScanQR --> ParseURL[Parse URL: /scan/id/]
    ParseURL --> CheckID{Instrument ID Valid?}
    
    CheckID -- Tidak --> Err404[Tampilkan Error 404]
    Err404 --> End1([Selesai])
    
    CheckID -- Ya --> CheckLogin{User Sudah Login?}
    
    CheckLogin -- Tidak --> SaveSess[Simpan instrument_id di Session]
    SaveSess --> RedLogin[Redirect ke /login/?next=/scan/id/]
    RedLogin --> ProcLogin[Proses Login]
    
    CheckLogin -- Ya --> GetCert[Ambil Sertifikat Terbaru]
    GetCert --> LogAccess[Catat Access Log action=view]
    
    LogAccess --> ShowRes[Tampilkan Scan Result]
    ProcLogin --> ShowRes
    
    ShowRes --> End2([Selesai])
```

---

## 4. Flowchart Manajemen Instrumen

```mermaid
flowchart TD
    Start([Mulai]) --> AksesList[Akses Halaman Daftar Instrumen]
    AksesList --> ChooseAct{Pilih Aksi?}
    
    ChooseAct -- Tambah Baru --> ShowForm[Tampilkan Form Tambah Instrumen]
    ShowForm --> InputData[/Isi Data Instrumen/]
    InputData --> CheckValid{Valid?}
    CheckValid -- Tidak --> ErrMsg[Tampilkan Error]
    ErrMsg --> InputData
    CheckValid -- Ya --> SaveDB[Simpan Database + Auto Gen QR Code]
    
    ChooseAct -- Lihat Detail --> ShowDetail[Tampilkan Detail Instrumen]
    ShowDetail --> SubAct{Sub Aksi?}
    SubAct -- Edit --> FormEdit[Form Edit] --> SaveEdit[Simpan Perubahan]
    SubAct -- Hapus --> ConfirmDel[Konfirmasi Hapus] --> CheckDel{Yakin?}
    CheckDel -- Ya --> DoDel[Hapus Data]
    SubAct -- Regen QR --> RegenQR[Generate Ulang QR]
    SubAct -- Print QR --> PrintQR[Halaman Print QR]
    
    ChooseAct -- Cari/Filter --> ExecSearch[Eksekusi Pencarian]
    ExecSearch --> ShowRes[Tampilkan Hasil]
    
    SaveDB --> End([Selesai])
    SaveEdit --> ShowDetail
    DoDel --> AksesList
    RegenQR --> ShowDetail
    PrintQR --> End
    ShowRes --> End
```

---

## 5. Flowchart Manajemen Sertifikat

```mermaid
flowchart TD
    Start([Mulai]) --> AksesList[Akses Halaman Daftar Sertifikat]
    AksesList --> ChooseAct{Pilih Aksi?}
    
    ChooseAct -- Tambah Baru --> ShowForm[Tampilkan Form Tambah Sertifikat]
    ShowForm --> InputData[/Isi Data & Upload PDF/]
    InputData --> CheckValid{Valid?}
    CheckValid -- Tidak --> ErrMsg[Tampilkan Error]
    ErrMsg --> InputData
    CheckValid -- Ya --> SaveDB[Simpan Database]
    
    ChooseAct -- Lihat Detail --> ShowDetail[Tampilkan Detail + Catat Access Log]
    ShowDetail --> SubAct{Sub Aksi?}
    SubAct -- Edit --> FormEdit[Form Edit] --> SaveEdit[Simpan Perubahan]
    SubAct -- Hapus --> ConfirmDel[Konfirmasi Hapus] --> CheckDel{Yakin?}
    CheckDel -- Ya --> DoDel[Hapus Data]
    SubAct -- Download PDF --> CheckPDF{File PDF Ada?}
    CheckPDF -- Ya --> ServePDF[Serve File PDF + Catat Log]
    CheckPDF -- Tidak --> ErrPDF[Tampilkan Error]
    
    ChooseAct -- Filter/Cari --> ExecSearch[Filter Status/Teks]
    ExecSearch --> ShowRes[Tampilkan Hasil]
    
    SaveDB --> End([Selesai])
    SaveEdit --> ShowDetail
    DoDel --> AksesList
    ServePDF --> End
    ErrPDF --> ShowDetail
    ShowRes --> End
```

---

## 6. Flowchart Monitoring & Notifikasi Email

```mermaid
flowchart TD
    %% Monitoring
    Start1([Mulai Monitoring]) --> AksesMon[Akses Halaman Monitoring]
    AksesMon --> QueryLog[Query 100 Log Terbaru]
    QueryLog --> ShowTable[Tampilkan Tabel Log]
    ShowTable --> End1([Selesai])
    
    %% Notifikasi
    Start2([Mulai Notifikasi]) --> ClickNotif[Admin Klik Kirim Notifikasi]
    ClickNotif --> QueryExp[Query Sertifikat Expiring <= 7 hari]
    QueryExp --> CheckExp{Ada yang Expired?}
    
    CheckExp -- Ya --> LoopMail[Loop & Kirim Email]
    LoopMail --> ShowSucc[Pesan X Notifikasi Terkirim]
    CheckExp -- Tidak --> ShowZero[Pesan 0 Notifikasi Terkirim]
    
    ShowSucc --> RedDash[Redirect ke Dashboard]
    ShowZero --> RedDash
    RedDash --> End2([Selesai])
    
    %% Kelola User
    Start3([Mulai Kelola User]) --> AksesUser[Akses Manajemen Pengguna]
    AksesUser --> ShowUsers[Tampilkan Daftar UserProfile]
    ShowUsers --> CheckUnblock{Admin Klik Unblock?}
    
    CheckUnblock -- Ya --> DoUnblock[Reset failed_attempts=0, is_blocked=False]
    DoUnblock --> ShowMsg[Pesan User Di-unblock]
    
    CheckUnblock -- Tidak --> End3([Selesai])
    ShowMsg --> End3
```

---

## 7. Entity Relationship Diagram (ERD)

```mermaid
erDiagram
    User ||--|| UserProfile : "has"
    User ||--o{ AccessLog : "generates"
    Instrument ||--o{ Certificate : "has"
    Instrument ||--o{ AccessLog : "referenced in"
    Certificate ||--o{ AccessLog : "referenced in"

    User {
        int id PK
        string username
        string email
        string password
    }

    UserProfile {
        int id PK
        int user_id FK
        string nama_lengkap
        string instansi
        string role
        boolean is_blocked
        int failed_attempts
        datetime blocked_at
    }

    Instrument {
        uuid id PK
        string nama_alat
        string merk
        string nomor_seri UNIQUE
        string lokasi
        string qr_code
        datetime created_at
    }

    Certificate {
        uuid id PK
        uuid instrument_id FK
        string nomor_sertifikat UNIQUE
        date tanggal_kalibrasi
        date tanggal_berlaku
        string file_sertifikat
        boolean is_active
    }

    AccessLog {
        int id PK
        int user_id FK
        uuid instrument_id FK
        uuid certificate_id FK
        string action
        string ip_address
        datetime accessed_at
    }
```
