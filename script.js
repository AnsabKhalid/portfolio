// In-memory theme state (no localStorage)
let currentTheme = "dark";

// EmailJS Configuration - REPLACE THESE WITH YOUR ACTUAL VALUES
const EMAILJS_CONFIG = {
  publicKey: "cJoumGjE5bYHNjiTi",
  serviceId: "service_eczt61n",
  templateId: "template_pkmqi5i",
};

// Initialize EmailJS
(function () {
  emailjs.init(EMAILJS_CONFIG.publicKey);
})();

// Theme Management
class ThemeManager {
  constructor() {
    this.init();
  }

  init() {
    // Set initial theme
    this.setTheme(currentTheme);
    this.bindEvents();
  }

  setTheme(theme) {
    currentTheme = theme;
    if (theme === "dark") {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }

  toggleTheme() {
    const isDark = document.documentElement.classList.contains("dark");
    this.setTheme(isDark ? "light" : "dark");
  }

  bindEvents() {
    document.getElementById("theme-toggle").addEventListener("click", () => {
      this.toggleTheme();
    });
  }
}

// Mobile Menu Toggle Functionality
function setupMobileMenuToggle() {
  const mobileMenuToggle = document.getElementById("mobile-menu-toggle");
  const mobileMenu = document.getElementById("mobile-menu");
  const menuIcon = document.getElementById("menu-icon");
  const closeIcon = document.getElementById("close-icon");

  if (mobileMenuToggle && mobileMenu && menuIcon && closeIcon) {
    mobileMenuToggle.addEventListener("click", () => {
      // Toggle mobile menu visibility
      mobileMenu.classList.toggle("hidden");

      // Toggle between menu and close icons
      menuIcon.classList.toggle("hidden");
      closeIcon.classList.toggle("hidden");
    });

    // Close mobile menu when clicking on links
    const mobileLinks = mobileMenu.querySelectorAll("a");
    mobileLinks.forEach((link) => {
      link.addEventListener("click", () => {
        mobileMenu.classList.add("hidden");
        menuIcon.classList.remove("hidden");
        closeIcon.classList.add("hidden");
      });
    });
  }
}

// Notification system
function showNotification(message, type = "success") {
  const container = document.getElementById("notification-container");
  const notification = document.createElement("div");

  const iconSvg =
    type === "success"
      ? '<svg class="w-5 h-5 mr-2" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22,4 12,14.01 9,11.01"/></svg>'
      : '<svg class="w-5 h-5 mr-2" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>';

  notification.className = `p-4 rounded-lg shadow-lg mb-4 transition-all duration-300 transform translate-x-full ${
    type === "success" ? "bg-green-500 text-white" : "bg-red-500 text-white"
  }`;

  notification.innerHTML = `
                <div class="flex items-center">
                    ${iconSvg}
                    <span>${message}</span>
                </div>
            `;

  container.appendChild(notification);

  // Slide in
  setTimeout(() => {
    notification.classList.remove("translate-x-full");
  }, 100);

  // Remove after 5 seconds
  setTimeout(() => {
    notification.classList.add("translate-x-full");
    setTimeout(() => {
      if (notification.parentNode) {
        notification.parentNode.removeChild(notification);
      }
    }, 300);
  }, 5000);
}

// Form validation
function validateForm(formData) {
  const errors = [];

  if (!formData.from_name.trim()) errors.push("Name is required");
  if (!formData.from_email.trim()) errors.push("Email is required");
  if (
    formData.from_email &&
    !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.from_email)
  ) {
    errors.push("Please enter a valid email address");
  }
  if (!formData.subject.trim()) errors.push("Subject is required");
  if (!formData.message.trim()) errors.push("Message is required");

  return errors;
}

// Initialize everything when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  new ThemeManager();
  setupMobileMenuToggle();

  // Add smooth scrolling behavior
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute("href"));
      if (target) {
        target.scrollIntoView({
          behavior: "smooth",
        });
      }
    });
  });

  // Contact form submission with EmailJS
  const form = document.getElementById("contact-form");
  const sendBtn = document.getElementById("send-btn");

  form.addEventListener("submit", function (e) {
    e.preventDefault();

    // Get form data
    const formData = new FormData(form);
    const data = {};
    for (let [key, value] of formData.entries()) {
      data[key] = value;
    }

    // Validate form
    const errors = validateForm(data);
    if (errors.length > 0) {
      showNotification(errors[0], "error");
      return;
    }

    // Update button state
    const originalText = sendBtn.innerHTML;
    sendBtn.disabled = true;
    sendBtn.innerHTML =
      '<svg class="w-5 h-5 animate-spin inline mr-2" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 11-6.219-8.56"/></svg>Sending...';

    // Send email using EmailJS
    emailjs
      .send(EMAILJS_CONFIG.serviceId, EMAILJS_CONFIG.templateId, data)
      .then(function (response) {
        console.log("SUCCESS!", response.status, response.text);
        showNotification(
          "Message sent successfully! I'll get back to you soon.",
          "success"
        );
        form.reset();
      })
      .catch(function (error) {
        console.error("FAILED...", error);
        // Fallback for demo purposes - in real implementation, this would show the actual error
        if (EMAILJS_CONFIG.publicKey === "YOUR_PUBLIC_KEY") {
          showNotification(
            "EmailJS not configured. Please add your EmailJS credentials to enable email sending.",
            "error"
          );
        } else {
          showNotification(
            "Failed to send message. Please try again later or contact me directly.",
            "error"
          );
        }
      })
      .finally(function () {
        sendBtn.disabled = false;
        sendBtn.innerHTML = originalText;
      });
  });

  // Resume download functionality
  document
    .getElementById("download-resume")
    .addEventListener("click", function () {
      const link = document.createElement("a");
      link.href = "AnsabKhalid.pdf";
      link.download = "Ansab_Khalid_Resume.pdf";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      showNotification("Resume downloaded successfully!", "success");
    });

  // Add scroll effect to header
  const header = document.getElementById("header");
  let lastScrollY = window.scrollY;

  window.addEventListener("scroll", () => {
    const currentScrollY = window.scrollY;

    if (currentScrollY > 100) {
      header.classList.add("bg-white/95", "dark:bg-gray-900/95");
    } else {
      header.classList.remove("bg-white/95", "dark:bg-gray-900/95");
    }

    lastScrollY = currentScrollY;
  });

  // Add active navigation highlighting
  const sections = document.querySelectorAll("section[id]");
  const navLinks = document.querySelectorAll(".nav-link");

  function highlightNavigation() {
    let current = "";
    sections.forEach((section) => {
      const sectionTop = section.getBoundingClientRect().top;
      if (sectionTop <= 100) {
        current = section.getAttribute("id");
      }
    });

    navLinks.forEach((link) => {
      link.classList.remove("text-purple-600", "dark:text-purple-400");
      link.classList.add("text-gray-700", "dark:text-gray-300");

      if (link.getAttribute("href") === `#${current}`) {
        link.classList.remove("text-gray-700", "dark:text-gray-300");
        link.classList.add("text-purple-600", "dark:text-purple-400");
      }
    });
  }

  window.addEventListener("scroll", highlightNavigation);
  highlightNavigation(); // Run once on load

  // Add animation on scroll for project cards
  const observerOptions = {
    threshold: 0.1,
    rootMargin: "0px 0px -50px 0px",
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = "1";
        entry.target.style.transform = "translateY(0)";
      }
    });
  }, observerOptions);

  // Observe project cards and skill cards
  document
    .querySelectorAll(".group, .bg-gray-50.dark\\:bg-gray-800")
    .forEach((card) => {
      card.style.opacity = "0";
      card.style.transform = "translateY(20px)";
      card.style.transition = "opacity 0.6s ease, transform 0.6s ease";
      observer.observe(card);
    });

  // Projects Slider Functionality - RESPONSIVE
  const slider = document.getElementById("projects-slider");
  const prevBtn = document.getElementById("prev-btn");
  const nextBtn = document.getElementById("next-btn");
  const dotsContainer = document.getElementById("slider-dots");

  let currentSlide = 0;
  let slidesPerView = getSlidesPerView(); // Dynamic based on screen size
  const totalProjects = slider.children.length;
  let totalSlides = Math.ceil(totalProjects / slidesPerView);

  // Function to determine slides per view based on screen width
  function getSlidesPerView() {
    if (window.innerWidth < 768) {
      return 1; // Mobile: 1 slide
    } else {
      return 2; // Desktop/Tablet: 2 slides
    }
  }

  // Initialize dots
  function createDots() {
    dotsContainer.innerHTML = ""; // Clear existing dots
    for (let i = 0; i < totalSlides; i++) {
      const dot = document.createElement("button");
      dot.className = `w-3 h-3 rounded-full transition-colors ${
        i === 0 ? "bg-purple-600" : "bg-gray-300 dark:bg-gray-600"
      }`;
      dot.addEventListener("click", () => goToSlide(i));
      dotsContainer.appendChild(dot);
    }
  }

  function updateSlider() {
    // Calculate the translation percentage based on current slidesPerView
    const slideWidth = 100 / slidesPerView;
    const translateX = -(currentSlide * slideWidth * slidesPerView);
    slider.style.transform = `translateX(${translateX}%)`;

    // Update dots
    const dots = dotsContainer.querySelectorAll("button");
    dots.forEach((dot, index) => {
      dot.className = `w-3 h-3 rounded-full transition-colors ${
        index === currentSlide
          ? "bg-purple-600"
          : "bg-gray-300 dark:bg-gray-600"
      }`;
    });

    // Update button states
    prevBtn.disabled = currentSlide === 0;
    nextBtn.disabled = currentSlide === totalSlides - 1;
  }

  function goToSlide(slideIndex) {
    if (slideIndex >= 0 && slideIndex < totalSlides) {
      currentSlide = slideIndex;
      updateSlider();
    }
  }

  function nextSlide() {
    if (currentSlide < totalSlides - 1) {
      currentSlide++;
      updateSlider();
    }
  }

  function prevSlide() {
    if (currentSlide > 0) {
      currentSlide--;
      updateSlider();
    }
  }

  // Handle window resize
  let resizeTimeout;
  window.addEventListener("resize", () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => {
      const newSlidesPerView = getSlidesPerView();
      if (newSlidesPerView !== slidesPerView) {
        slidesPerView = newSlidesPerView;
        totalSlides = Math.ceil(totalProjects / slidesPerView);

        // Reset to first slide if current slide is out of bounds
        if (currentSlide >= totalSlides) {
          currentSlide = 0;
        }

        createDots();
        updateSlider();
      }
    }, 250);
  });

  // Event listeners
  nextBtn.addEventListener("click", nextSlide);
  prevBtn.addEventListener("click", prevSlide);

  // Auto-play slider
  let autoPlayInterval = setInterval(() => {
    if (currentSlide < totalSlides - 1) {
      nextSlide();
    } else {
      goToSlide(0);
    }
  }, 10000);

  // Pause auto-play on hover
  slider.parentElement.addEventListener("mouseenter", () => {
    clearInterval(autoPlayInterval);
  });

  // Resume auto-play when not hovering
  slider.parentElement.addEventListener("mouseleave", () => {
    autoPlayInterval = setInterval(() => {
      if (currentSlide < totalSlides - 1) {
        nextSlide();
      } else {
        goToSlide(0);
      }
    }, 4000);
  });

  // Initialize slider
  createDots();
  updateSlider();

  // Add keyboard navigation
  document.addEventListener("keydown", (e) => {
    if (e.key === "ArrowLeft") {
      prevSlide();
    } else if (e.key === "ArrowRight") {
      nextSlide();
    }
  });

  // Get the current year
  const currentYear = new Date().getFullYear();

  // Update the copyright year in the HTML
  document.getElementById(
    "copyright"
  ).innerHTML = `© ${currentYear} Full Stack Developer Portfolio. All rights reserved. Crafted with passion and modern technologies.`;
});
