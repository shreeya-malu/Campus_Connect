let domains = [];
let currentUser = null;

async function fetchDomains() {
  try {
    const response = await fetch("/get_domains");
    domains = await response.json();
    populateDomainDropdowns();
  } catch (error) {
    console.error("Error fetching domains:", error);
  }
}

async function checkSession() {
  try {
    const response = await fetch("/check_session");
    if (!response.ok) throw new Error("Session check failed");
    return await response.json();
  } catch (error) {
    console.error("Session check error:", error);
    return { logged_in: false };
  }
}


function showAdminPanel(requests) {
  const adminPanel = document.createElement("div");
  adminPanel.className = "admin-panel";
  adminPanel.innerHTML = `
    <h3>Pending Domain Requests</h3>
    ${
      requests.length === 0
        ? "<p>No pending requests</p>"
        : requests
            .map(
              (request) => `
        <div class="request-item" data-id="${request.request_id}">
          <p><strong>Domain:</strong> ${request.domain_name}</p>
          <p><strong>Requested by:</strong> ${request.requester_name}</p>
          <div class="request-actions">
            <button class="approve-btn">Approve</button>
            <button class="reject-btn">Reject</button>
          </div>
        </div>
      `
            )
            .join("")
    }
  `;

  // Add to profile details
  const profileDetails = document.querySelector(".profile-details");
  profileDetails.appendChild(adminPanel);

}



function showNotification(message, isError = false) {
  // Create notification element if it doesn't exist
  let notification = document.getElementById("notification");

  if (!notification) {
    notification = document.createElement("div");
    notification.id = "notification";
    document.body.appendChild(notification);
  }

  notification.textContent = message;
  notification.className = isError ? "error" : "success";

  // Show the notification
  notification.style.display = "block";

  // Auto-hide after 5 seconds
  setTimeout(() => {
    notification.style.display = "none";
  }, 5000);
}

function setupRequestHandlers() {
  const requestForms = document.querySelectorAll(".request-actions form");
  if (requestForms.length === 0) return;

  // Create status dialog elements if they don't exist
  if (!document.getElementById("status-dialog")) {
    const dialog = document.createElement("div");
    dialog.id = "status-dialog";
    dialog.className = "dialog-box";
    dialog.style.cssText =
      "display: none; position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); z-index: 10000;";
    dialog.innerHTML = `
      <p id="status-message"></p>
      <button onclick="location.reload()">OK</button>
    `;
    document.body.appendChild(dialog);
  }

  requestForms.forEach((form) => {
    form.addEventListener("submit", async function (e) {
      e.preventDefault();

      const formData = new FormData(this);
      const actionUrl = this.action;

      try {
        const response = await fetch(actionUrl, {
          method: "POST",
          body: formData,
        });

        const result = await response.json();

        // Show dialog with result
        const dialog = document.getElementById("status-dialog");
        const message = document.getElementById("status-message");
        message.textContent =
          result.message || `Request ${formData.get("action")}d successfully`;
        dialog.style.display = "block";
      } catch (error) {
        console.error("Error:", error);
        alert("An error occurred. Please try again.");
      }
    });
  });
}

//  handleRequestAction function to use the dialog
async function handleRequestAction(button, action, requestId) {
  try {
    button.disabled = true;
    const response = await fetch(`/admin/handle_domain/${requestId}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: `action=${action}`,
    });

    if (response.ok) {
      const result = await response.json();
      showNotification(`Request ${action}d successfully!`);
      // Refresh after 2 seconds to show updated status
      setTimeout(() => location.reload(), 2000);
    } else {
      const error = await response.json();
      showNotification(error.message || `Failed to ${action} request`, true);
      button.disabled = false;
    }
  } catch (error) {
    console.error("Error:", error);
    showNotification("An error occurred. Please try again.", true);
    button.disabled = false;
  }
}

function populateDomainDropdowns() {
  const searchDomain = document.getElementById("searchDomain");
  const contributeDomain = document.getElementById("contributeDomain");

  [searchDomain, contributeDomain].forEach((dropdown) => {
    // Clear existing options except the first one
    while (dropdown.options.length > 1) {
      dropdown.remove(1);
    }

    // Add fetched domains
    domains.forEach((domain) => {
      const option = document.createElement("option");
      option.value = domain;
      option.textContent = domain;
      dropdown.appendChild(option);
    });
  });
}

function setupDomainToggle() {
  const toggleBtn = document.getElementById("toggleDomainBtn");
  const domainSelect = document.getElementById("contributeDomain"); // Changed to use contributeDomain
  const newDomainInput = document.getElementById("newDomainInput");

  toggleBtn.addEventListener("click", () => {
    if (newDomainInput.style.display === "none") {
      // Switch to add new domain mode
      domainSelect.style.display = "none";
      newDomainInput.style.display = "block";
      toggleBtn.textContent = "✓";
      newDomainInput.focus();
    } else {
      // Add new domain and switch back
      const newDomain = newDomainInput.value.trim();
      if (newDomain && !domains.includes(newDomain)) {
        domains.unshift(newDomain); // Add to beginning
        populateDomainDropdowns();
        domainSelect.value = newDomain;

        // Send to backend (you'll need to implement this endpoint)
        fetch("/add_domain", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ domain: newDomain }),
        });
      }

      // Reset UI
      newDomainInput.value = "";
      newDomainInput.style.display = "none";
      domainSelect.style.display = "block";
      toggleBtn.textContent = "+";
    }
  });

  newDomainInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
      toggleBtn.click();
    }
  });
}

function showContribute() {
  document.getElementById("contribute-form").style.display = "block";
  document.getElementById("search-form").style.display = "none";
}

function showSearch() {
  document.getElementById("contribute-form").style.display = "none";
  document.getElementById("search-form").style.display = "block";
}

// Attach flipping only to the front face
document.querySelectorAll(".card-front").forEach((front) => {
  front.addEventListener("click", function (e) {
    const card = front.closest(".resource-card");
    card.classList.add("flipped");
  });
});

// Prevent unintentional flipping when interacting with inputs (no toggle on input clicks)
document.querySelectorAll(".card-back input").forEach((input) => {
  input.addEventListener("click", function (e) {
    e.stopPropagation(); // Prevents bubbling up the click to card
  });
});

// Fetch and display resources from backend when Search is clicked
async function fetchResources() {
  const yearSelect = document.getElementById("searchYear");
  const domainSelect = document.getElementById("searchDomain"); // This now correctly points to search form's domain select
  const resultsGrid = document.getElementById("results-grid");

  // Get the selected values properly
  const year = yearSelect.value;
  const domain = domainSelect.value;

  // Debug logging
  console.log("Searching with:", { year, domain });

  // Clear previous results with a loading message
  resultsGrid.innerHTML = "<p>Searching for resources...</p>";

  // Validation
  if (!year || year === "" || !domain || domain === "") {
    resultsGrid.innerHTML =
      '<p class="error-message">Please select both year and domain</p>';
    return;
  }

  try {
    const response = await fetch("/search_resource", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({
        year: year,
        domain: domain,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(
        errorData.error || `HTTP error! status: ${response.status}`
      );
    }

    const data = await response.json();
    displayResources(data);
  } catch (error) {
    console.error("Error fetching resources:", error);
    resultsGrid.innerHTML = `
      <p class="error-message">${
        error.message || "Error loading resources. Please try again."
      }</p>
    `;
  }
}

function displayResources(data) {
  const resultsGrid = document.getElementById("results-grid");
  resultsGrid.innerHTML = "";

  const groupedData = data.reduce((acc, item) => {
    const type = item.ResourceType || "General";
    if (!acc[type]) acc[type] = [];
    acc[type].push(item.Link);
    return acc;
  }, {});

  const icons = {
    "Previous Year Papers": "/static/images/previous_papers.jpg",
    "Reference Books": "/static/images/reference_books.jpg",
    "Research Papers": "/static/images/research_paper.jpg",
    "Youtube Videos": "/static/images/youtube_links.png",
    "Study Notes": "/static/images/study_notes.jpg",
    "Related Projects": "/static/images/related_projects.jpg",
    "Internships/Job Specific": "/static/images/internships.jpg",
    Quizzes: "/static/images/quizzes.jpg",
    "MOOCs Platforms": "/static/images/moocs.jpg",
  };

  Object.entries(groupedData).forEach(([title, links]) => {
    const card = document.createElement("div");
    card.className = "resource-card";

    const inner = document.createElement("div");
    inner.className = "card-inner";

    const front = document.createElement("div");
    front.className = "card-front";
    front.innerHTML = `
      <img src="${icons[title] || "/static/images/default.jpg"}" alt="${title}">
      <p>${title}</p>
    `;

    const back = document.createElement("div");
    back.className = "card-back";
    back.innerHTML = `
      <strong>${title} Links:</strong>
      <ul>
        ${links
          .map(
            (link) => `
          <li>
            <button onclick="window.open('${link}', '_blank')" class="link-btn">
              Open Resource
            </button>
          </li>
        `
          )
          .join("")}
      </ul>
    `;

    inner.appendChild(front);
    inner.appendChild(back);
    card.appendChild(inner);

    card.addEventListener("click", function () {
      this.classList.toggle("flipped");
    });

    resultsGrid.appendChild(card);
  });
}

// Navigation to requests page
async function navigateToRequests() {
  try {
    // Verify session first
    const sessionData = await checkSession();

    if (!sessionData.logged_in) {
      window.location.href = "/login";
      return;
    }

    if (sessionData.user?.role === "admin") {
      window.location.href = "/admin/requests";
    } else {
      window.location.href = "/request-status";
    }
  } catch (error) {
    console.error("Navigation error:", error);
    window.location.href = "/login";
  }
}

async function submitContribution(event) {
  event.preventDefault();

  // First check if user is logged in at all
  const sessionResponse = await fetch("/check_session");
  const sessionData = await sessionResponse.json();

  if (!sessionData.logged_in) {
    showNotification("Please login to contribute resources.", true);
    window.location.href = "/login";
    return;
  }

  // Then check if user is a guest
  if (
    sessionData.user &&
    (sessionData.user.role === "guest" || sessionData.is_guest)
  ) {
    showNotification(
      "Guests are not allowed to contribute resources. Please login with a student account.",
      true
    );
    return;
  }

  const form = event.target;
  const name = form.querySelector('input[name="name"]').value;
  const year = form.querySelector('select[name="year"]').value;
  const domain = form.querySelector('select[name="domain"]').value;

  const resourceCards = form.querySelectorAll(".resource-card");
  const resources = [];

  resourceCards.forEach((card) => {
    if (card.classList.contains("flipped")) {
      const type = card.querySelector(".card-front p").innerText.trim();
      const linkInput = card
        .querySelector(".card-back input[type='url']")
        .value.trim();
      if (linkInput) {
        resources.push({ type: type, link: linkInput });
      }
    }
  });

  if (resources.length === 0) {
    showNotification(
      "Please enter at least one valid resource link by clicking on cards and adding URLs!",
      true
    );
    return;
  }

  const payload = {
    name: name,
    year: year,
    domain: domain,
    resources: resources,
  };

  try {
    const response = await fetch("/add_resource", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const result = await response.json();

    if (response.status === 400 && result.requires_approval) {
      showNotification(
        "Your domain request has been sent to admin. Resources will be added after approval."
      );
      resetContributionForm(form);
      return;
    }

    if (response.ok) {
      showNotification("Resources added successfully!");
      resetContributionForm(form);
    } else {
      showNotification(result.error || "Failed to add resources", true);
    }
  } catch (error) {
    console.error("Submission error:", error);
    showNotification(`Error: ${error.message}`, true);
  }
}

function showStatusDialog(message) {
  // Create dialog if it doesn't exist
  if (!document.getElementById("status-dialog")) {
    const dialog = document.createElement("div");
    dialog.id = "status-dialog";
    dialog.className = "dialog-box";
    dialog.style.cssText =
      "display: none; position: fixed; top: 0; left: 0; width: 100%; z-index: 10000; border-radius: 0 0 10px 10px;";
    dialog.innerHTML = `
      <p id="status-message"></p>
      <button onclick="document.getElementById('status-dialog').style.display='none'">OK</button>
    `;
    document.body.appendChild(dialog);
  }

  const dialog = document.getElementById("status-dialog");
  const messageElement = document.getElementById("status-message");
  messageElement.textContent = message;
  dialog.style.display = "block";

  // Auto-hide after 5 seconds
  setTimeout(() => {
    dialog.style.display = "none";
  }, 5000);
}
function resetContributionForm(form) {
  // Reset form fields
  form.reset();

  // Unflip all cards
  document.querySelectorAll(".resource-card.flipped").forEach((card) => {
    card.classList.remove("flipped");
  });

  // Clear all link inputs
  document.querySelectorAll(".card-back input[type='url']").forEach((input) => {
    input.value = "";
  });
}

// Attach event listener for contribute form submission
document
  .querySelector("#contribute-form form")
  .addEventListener("submit", submitContribution);

// Profile Drawer Functionality
document.addEventListener("DOMContentLoaded", function () {
  const profileSection = document.querySelector("#profile-section");
  const profileIcon = document.querySelector(".profile-icon");
  const drawerClose = document.querySelector(".drawer-close");
  const overlay = document.querySelector(".profile-overlay");

  // Toggle drawer when clicking profile icon
  profileIcon.addEventListener("click", function (e) {
    e.stopPropagation();
    profileSection.classList.add("active");
  });

  // Close drawer when clicking close button
  drawerClose.addEventListener("click", function () {
    profileSection.classList.remove("active");
  });

  // Close drawer when clicking outside
  overlay.addEventListener("click", function () {
    profileSection.classList.remove("active");
  });

  // Close drawer when pressing Escape key
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      profileSection.classList.remove("active");
    }
  });
});
