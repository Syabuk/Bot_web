// Telegram WebApp инициализация
const tg = window.Telegram?.WebApp;

if (tg) {
  tg.expand();
  tg.ready();
  tg.enableClosingConfirmation();

  // Настройка основной кнопки
  tg.MainButton.setText("Обновить");
  tg.MainButton.onClick(() => {
    window.location.reload();
  });
  tg.MainButton.show();
}

// Мобильное меню
document.addEventListener("DOMContentLoaded", () => {
  const menuToggle = document.getElementById("menuToggle");
  const closeMenu = document.getElementById("closeMenu");
  const sidebar = document.getElementById("sidebar");
  const overlay = document.getElementById("overlay");
  const refreshLink = document.getElementById("refreshLink");
  const closeLink = document.getElementById("closeLink");

  if (menuToggle) {
    menuToggle.addEventListener("click", () => {
      sidebar.classList.add("open");
      overlay.classList.add("active");
    });
  }

  if (closeMenu) {
    closeMenu.addEventListener("click", () => {
      sidebar.classList.remove("open");
      overlay.classList.remove("active");
    });
  }

  if (overlay) {
    overlay.addEventListener("click", () => {
      sidebar.classList.remove("open");
      overlay.classList.remove("active");
    });
  }

  if (refreshLink) {
    refreshLink.addEventListener("click", (e) => {
      e.preventDefault();
      window.location.reload();
    });
  }

  if (closeLink && tg) {
    closeLink.addEventListener("click", (e) => {
      e.preventDefault();
      tg.close();
    });
  }
});

// Уведомления
function showNotification(title, message) {
  if (tg && tg.showPopup) {
    tg.showPopup({
      title: title,
      message: message,
      buttons: [{ type: "ok" }],
    });
  } else {
    alert(`${title}: ${message}`);
  }
}

// Скачивание файла с прогрессом
async function downloadFile(url, filename) {
  try {
    showNotification("Скачивание", `Начинается скачивание файла "${filename}"`);

    const response = await fetch(url);
    const blob = await response.blob();
    const link = document.createElement("a");
    const objectUrl = URL.createObjectURL(blob);

    link.href = objectUrl;
    link.download = filename;
    link.click();

    URL.revokeObjectURL(objectUrl);

    showNotification("Успех", `Файл "${filename}" успешно скачан!`);
  } catch (error) {
    console.error("Ошибка скачивания:", error);
    showNotification("Ошибка", "Не удалось скачать файл");
  }
}

// Плавная прокрутка
document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
  anchor.addEventListener("click", function (e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute("href"));
    if (target) {
      target.scrollIntoView({ behavior: "smooth" });
    }
  });
});

// Обработка жестов
let touchStartX = 0;
let touchEndX = 0;

document.addEventListener("touchstart", (e) => {
  touchStartX = e.changedTouches[0].screenX;
});

document.addEventListener("touchend", (e) => {
  touchEndX = e.changedTouches[0].screenX;
  handleSwipe();
});

function handleSwipe() {
  const sidebar = document.getElementById("sidebar");
  const overlay = document.getElementById("overlay");
  const swipeDistance = touchEndX - touchStartX;

  if (Math.abs(swipeDistance) > 50) {
    if (swipeDistance > 0 && touchStartX < 50) {
      // Свайп вправо - открыть меню
      if (sidebar && overlay) {
        sidebar.classList.add("open");
        overlay.classList.add("active");
      }
    } else if (swipeDistance < 0 && sidebar?.classList.contains("open")) {
      // Свайп влево - закрыть меню
      sidebar.classList.remove("open");
      overlay.classList.remove("active");
    }
  }
}

// Предзагрузка изображений
function preloadImages() {
  const images = document.querySelectorAll("img");
  images.forEach((img) => {
    const src = img.getAttribute("data-src");
    if (src) {
      img.src = src;
    }
  });
}

// Оптимизация производительности
if ("IntersectionObserver" in window) {
  const imageObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const img = entry.target;
        const src = img.getAttribute("data-src");
        if (src) {
          img.src = src;
          imageObserver.unobserve(img);
        }
      }
    });
  });

  document.querySelectorAll("img[data-src]").forEach((img) => {
    imageObserver.observe(img);
  });
}

// Обработка ошибок
window.addEventListener("error", (e) => {
  console.error("Global error:", e.error);
  if (tg && tg.showPopup) {
    tg.showPopup({
      title: "Ошибка",
      message: "Произошла ошибка. Попробуйте обновить страницу.",
      buttons: [{ type: "ok" }],
    });
  }
});

// Сохранение состояния
let scrollPosition = 0;
window.addEventListener("beforeunload", () => {
  scrollPosition = window.scrollY;
  sessionStorage.setItem("scrollPosition", scrollPosition);
});

window.addEventListener("load", () => {
  const savedPosition = sessionStorage.getItem("scrollPosition");
  if (savedPosition) {
    window.scrollTo(0, parseInt(savedPosition));
  }
});
