(() => {
  const S = window.SITE || {};
  const reduzir = matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Vídeos dos projetos: só carregam e tocam quando aparecem na tela
  const videos = document.querySelectorAll("video[data-src]");
  const vio = new IntersectionObserver((es) => es.forEach(({ target: v, isIntersecting }) => {
    if (isIntersecting) {
      if (!v.src) v.src = v.dataset.src;
      if (!reduzir) v.play().catch(() => {});
    } else v.pause();
  }), { threshold: 0.35 });
  videos.forEach((v) => vio.observe(v));

  // Revelar ao rolar
  const rio = new IntersectionObserver((es) => es.forEach((e) => {
    if (e.isIntersecting) { e.target.classList.add("visto"); rio.unobserve(e.target); }
  }), { threshold: 0.15 });
  document.querySelectorAll(".revelar").forEach((el) => rio.observe(el));

  // Topo e luz que segue o mouse
  const topo = document.querySelector(".topo");
  addEventListener("scroll", () => topo.classList.toggle("rolou", scrollY > 30), { passive: true });
  const luz = document.querySelector(".luz-mouse");
  if (luz && !reduzir && matchMedia("(pointer: fine)").matches) {
    addEventListener("pointermove", (e) => {
      luz.style.transform = `translate(${e.clientX - 300}px, ${e.clientY - 300}px)`;
    }, { passive: true });
  } else if (luz) luz.remove();

  // Telas do topo se inclinam com o mouse
  const vitrine = document.querySelector(".vitrine");
  if (vitrine && !reduzir && matchMedia("(pointer: fine)").matches) {
    addEventListener("pointermove", (e) => {
      const x = e.clientX / innerWidth - 0.5, y = e.clientY / innerHeight - 0.5;
      vitrine.style.setProperty("--rx", `${(-y * 6).toFixed(2)}deg`);
      vitrine.style.setProperty("--ry", `${(x * 8).toFixed(2)}deg`);
    }, { passive: true });
  }

  // Contato
  const num = String((S.whatsapp && S.whatsapp.numero) || "").replace(/\D/g, "");
  if (num) document.querySelectorAll(".whats-link").forEach((a) => {
    a.href = `https://wa.me/${num}?text=${encodeURIComponent(S.whatsapp.mensagem || "")}`;
    a.hidden = false;
  });
  if (S.email) document.querySelectorAll(".email-link").forEach((a) => { a.href = `mailto:${S.email}`; a.hidden = false; });
  document.querySelectorAll("[data-ano]").forEach((el) => (el.textContent = new Date().getFullYear()));
})();
