  window.onload = function () {
    const signinTab = document.getElementById("signin-tab");
    const signupTab = document.getElementById("signup-tab");
    const signinForm = document.getElementById("signin-form");
    const signupForm = document.getElementById("signup-form");

    // Toggle between tabs
    signinTab.addEventListener("click", function () {
      signinTab.classList.add("active");
      signupTab.classList.remove("active");
      signinForm.classList.add("active");
      signupForm.classList.remove("active");
    });

    signupTab.addEventListener("click", function () {
      signupTab.classList.add("active");
      signinTab.classList.remove("active");
      signupForm.classList.add("active");
      signinForm.classList.remove("active");
    });

    document.querySelector(".switch-tab").addEventListener("click", function () {
      signupTab.click();
    });

    // Guest Login
    document.getElementById("guestlogin-btn").addEventListener("click", function (event) {
      event.preventDefault();

      const guestData = {
        email: "guest@gmail.com",
        password: "guest123",
        is_guest: true
      };

      fetch("/signin", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(guestData)
      })
        .then(res => res.json())
        .then(data => {
          if (data.message) {
            alert(data.message);
            localStorage.setItem('is_guest', data.is_guest); // Save guest status
            window.location.href = "/"; // Redirect to homepage
          } else {
            alert(data.error || "Login failed");
          }
        })
        .catch(err => {
          console.error("Guest login failed:", err);
          alert("Something went wrong.");
        });
    });


  // Sign In Submit
  signinForm.addEventListener("submit", function(event) {
    event.preventDefault();
  
    const email = document.getElementById("signin-email").value;
    const password = document.getElementById("signin-password").value;
  
    fetch("/signin", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password, is_guest: false })
    })
    .then(response => {
      if (!response.ok) {
        return response.json().then(err => { throw err; });
      }
      return response.json();
    })
    .then(data => {
      if (data.error) {
        alert(data.error);
      } else {
        
        window.location.href = "/?login=success";
      }
    })
    .catch(error => {
      console.error("Error:", error);
      alert(error.error || "Login failed. Please try again.");
    });
  });
    // Sign Up Submit
    signupForm.addEventListener("submit", function (event) {
      event.preventDefault();

      const name = document.getElementById("signup-name").value;
      const email = document.getElementById("signup-email").value;
      const password = document.getElementById("signup-password").value;
      const passing_date = document.getElementById("signup-passing-date").value;
      const branch = document.getElementById("signup-branch").value;
      const role = document.getElementById("signup-role").value;

      fetch("/signup", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ name, email, password, passing_date, branch, role })
      })
        .then(res => res.json())
        .then(data => {
          if (data.message) {
            alert(data.message);
            signinTab.click(); // Switch to sign in after success
          } else {
            alert(data.error || "Signup failed");
          }
        })
        .catch(err => {
          console.error("Signup error:", err);
          alert("Something went wrong.");
        });

        function updateNavbar(user) {
          const authButtons = document.getElementById("auth-buttons");
          authButtons.innerHTML = `
            <div class="user-profile">
              <div class="profile-icon">
                <img src="/static/images/profile-icon.png" alt="Profile">
              </div>
              <div class="profile-details">
                <p><strong>${user.name}</strong></p>
                <p>${user.role}</p>
                ${user.branch ? `<p>${user.branch}</p>` : ''}
                ${user.year ? `<p>Year: ${user.year}</p>` : ''}
              </div>
            </div>
          `;
        }
    });
  };