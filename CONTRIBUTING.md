# 🤝 Katkıda Bulunma Rehberi

Bu proje, açık kaynak topluluğunun gücüne inanır ve her türlü katkıyı memnuniyetle karşılar. Projenin gelişimine yardımcı olmak isterseniz, bu rehberi okumanız rica olunur.

## 🌟 Nasıl Katkıda Bulunabilirsiniz?

Aşağıdaki yollarla projemize katkıda bulunabilirsiniz:

1.  **Hata Raporlama:** Bir hata (bug) bulursanız, lütfen bir [GitHub Issue](https://github.com/Metrohan/TechEventRadar/issues) açın. Hatayı mümkün olduğunca detaylı açıklayın:
    * Hatayı nasıl tekrar oluşturabileceğinizi (adım adım).
    * Beklenen davranışın ne olduğunu.
    * Gerçekleşen davranışın ne olduğunu.
    * Kullandığınız ortam (işletim sistemi, Python sürümü, bağımlılık sürümleri).
    * Varsa ekran görüntüleri veya hata logları.

2.  **Özellik Önerileri:** Yeni bir özellik veya iyileştirme fikriniz varsa, lütfen yine bir [GitHub Issue](https://github.com/Metrohan/TechEventRadar/issues) açın. Fikrinizi açıklayın ve neden faydalı olacağını belirtin.

3.  **Kod Katkısı (Pull Request):** Mevcut hataları düzeltmek veya yeni özellikler eklemek için kod yazmak isterseniz aşağıdaki adımları izleyin.

4.  **Dokümantasyon İyileştirmeleri:** README, bu dosya (`CONTRIBUTING.md`) veya kod yorumlarındaki eksiklikleri veya yanlışları düzeltmek de değerli bir katkıdır.

5.  **Starlama, Watchlama ve Paylaşma:** Bu projeyi bootcamp, hackathon gibi etkinlikleri arayan öğrenci veya bu sektöre girmek isteyen arkadaşlar için yaptım. Onların bu projeden haberdar olması için projeyi starlamanız ve paylaşmanız büyük önem arz ediyor. 

## 👨‍💻 Kod Katkısı Süreci

Kod ile katkıda bulunmak isterseniz, lütfen bu adımları takip edin:

1.  **Repoyu Fork edin:** Projenin GitHub reposunu kendi hesabınıza fork edin.
2.  **Repoyu Klonlayın:** Fork ettiğiniz repoyu yerel makinenize klonlayın.
    ```bash
    git clone https://github.com/Metrohan/TechEventRadar.git
    cd TechEventRadar
    ```
3.  **Bağımlılıkları Yükleyin:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Yeni Bir Branch Oluşturun:** Yaptığınız değişikliklere özel, anlamlı bir isimle yeni bir branch oluşturun.
    * Hata düzeltmeleri için: `fix/hata-adi` (örn: `fix/favicon-import-error`)
    * Yeni özellikler için: `feat/ozellik-adi` (örn: `feat/search-bar`)
    * Diğer iyileştirmeler için: `chore/iyilestirme-adi` (örn: `chore/code-refactor`)
    ```bash
    git checkout -b branch-adiniz
    ```
5.  **Değişikliklerinizi Yapın:** Kodunuzu yazın ve değişikliklerinizi test edin.
    * Yeni özellikler için test yazmaya çalışın.
    * Mevcut testleri bozmadığınızdan emin olun.
    * Kodlama standartlarına uymaya özen gösterin.

6.  **Değişikliklerinizi Commit Edin:** Yaptığınız değişiklikleri açıklayan anlamlı ve özlü commit mesajları kullanın. Her commit, tek bir mantıksal değişikliği temsil etmelidir.
    ```bash
    git add .
    git commit -m "feat: Eklenen özelliğin kısa açıklaması"
    # veya
    git commit -m "fix: Düzeltilen hatanın kısa açıklaması"
    ```
    *Commit mesajı formatı için [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) önerilir.*

7.  **Değişiklikleri Push'layın:**
    ```bash
    git push origin branch-adiniz
    ```
8.  **Pull Request Oluşturun:** GitHub'da, fork ettiğiniz repodan ana repoya (upstream) yeni bir PR oluşturun.
    * PR başlığı anlaşılır ve öz olsun.
    * Açıklama kısmında, ne tür değişiklikler yaptığınızı, neden yaptığınızı ve varsa ilgili GitHub Issue'ya referans verin (`Fixes #123`, `Closes #456`).
    * Ekran görüntüleri veya demolar eklemek, değişikliklerinizi anlamamıza yardımcı olabilir.

## 💡 Kodlama Standartları

* **PEP 8:** Python kodu için [PEP 8](https://www.python.org/dev/peps/pep-0008/) stil rehberine uymaya çalışın.
* **Anlaşılır Kod:** Kodunuzun temiz, okunabilir ve iyi yorumlanmış olmasına dikkat edin.
* **Docstrings:** Karmaşık fonksiyonlar veya modüller için Docstring (belgeleme dizeleri) eklemeyi düşünün.

## 🙏 Teşekkürler!

Bu projeye göstereceğiniz ilgi ve katkılarınız için şimdiden teşekkür ederiz. Birlikte daha iyiye!

---