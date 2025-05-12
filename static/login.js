// Auth functions
function checkLoginStatus() {
  fetch('/check_session')
    .then(response => response.json())
    .then(data => {
      const loginBtn = document.getElementById('login-btn');
      const profileSection = document.getElementById('profile-section');
      const profileIcon = document.getElementById('toggle-dashboard');

      if (data.logged_in && data.user) {
        // Logged in: Show profile section, hide login button
        loginBtn.style.display = 'none';
        profileSection.style.display = 'block';
        profileIcon.style.display = 'block';  // Ensure profile icon is visible when logged in

        // Set user info in the profile section
        document.getElementById('profile-name').textContent = data.user.name;
        document.getElementById('profile-role').textContent = data.user.role;
        document.getElementById('profile-branch').textContent = data.user.branch || '';

        // Attach logout functionality
        document.getElementById('logout-btn').addEventListener('click', function() {
          fetch('/logout', { method: 'POST' })
            .then(() => {
              // After logout, show login button and hide profile section
              loginBtn.style.display = 'block';
              profileSection.style.display = 'none';
              profileIcon.style.display = 'none'; // Hide profile icon after logout
              window.location.reload(); // Reload to reset the state
            });
        });

        // Attach check request functionality
        document.getElementById('check-request-btn').addEventListener('click', function() {
          fetch('/check_session')
            .then(response => response.json())
            .then(sessionData => {
              if (sessionData.logged_in) {
                if (sessionData.user.role === 'admin') {
                  window.location.href = '/admin/requests';
                } else {
                  window.location.href = '/request-status';
                }
              } else {
                window.location.href = '/login';
              }
            })
            .catch(error => {
              console.error('Error verifying session:', error);
              window.location.href = '/login';
            });
        });
      } else {
        // Logged out: Show login button and hide profile section
        loginBtn.style.display = 'block';
        profileSection.style.display = 'none';
        loginBtn.textContent = 'Login/Sign up';
        loginBtn.onclick = function() { window.location.href = '/login'; };

        // Hide profile icon when logged out
        profileIcon.style.display = 'none';
      }
    })
    .catch(error => {
      console.error('Error checking initial session status:', error);
      document.getElementById('login-btn').style.display = 'block';
      document.getElementById('profile-section').style.display = 'none';
    });
}

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
  // Initial session check
  checkLoginStatus();
  
  // Periodic session check (every 5 minutes)
  setInterval(checkLoginStatus, 300000);
  
  // Other initializations
  fetchDomains();
  setupDomainToggle();
  
  // Event delegation for dynamic elements
 document.addEventListener('click', function(e) {
    // Handle profile icon click
    if (e.target.closest('.profile-icon')) {
      const profileSection = document.getElementById('profile-section');
      if (profileSection) {
        profileSection.style.display = profileSection.style.display === 'flex' ? 'none' : 'flex';
      }
    }
    
    // Handle clicks outside profile to close it
    if (!e.target.closest('#profile-section') && !e.target.closest('.profile-icon')) {
      const profileSection = document.getElementById('profile-section');
    }
  });
  
  // Make sure login button works
  document.getElementById('login-btn')?.addEventListener('click', function() {
    window.location.href = '/login';
  });
});



async function checkLoginStatus() {
  try {
    const sessionData = await checkSession();
    currentUser = sessionData.user || null;
    
    const loginBtn = document.getElementById('login-btn');
    const profileSection = document.getElementById('profile-section');
    const profileIcon = document.querySelector('.profile-icon');
    
    if (sessionData.logged_in && currentUser) {
      // User is logged in
      if (loginBtn) loginBtn.style.display = 'none';
      if (profileSection) profileSection.style.display = 'flex';
      if (profileIcon) profileIcon.style.display = 'block';
      
      // Update profile info
      if (document.getElementById('profile-name')) {
        document.getElementById('profile-name').textContent = currentUser.name;
        document.getElementById('profile-role').textContent = currentUser.role;
        document.getElementById('profile-branch').textContent = currentUser.branch || '';
      }
      
      // Setup logout button
      document.getElementById('logout-btn')?.addEventListener('click', logoutUser);
      
      // Setup request status button
      document.getElementById('check-request-btn')?.addEventListener('click', navigateToRequests);
      
    } else {
      // User is not logged in
      if (loginBtn) {
        loginBtn.style.display = 'block';
        loginBtn.textContent = 'Login/Sign up';
        loginBtn.onclick = () => window.location.href = '/login';
      }
      if (profileSection) profileSection.style.display = 'none';
      if (profileIcon) profileIcon.style.display = 'none';
    }
  } catch (error) {
    console.error('Login status check failed:', error);
    // Fallback to showing login button
    const loginBtn = document.getElementById('login-btn');
    if (loginBtn) { 
      loginBtn.style.display = 'block';
      loginBtn.textContent = 'Login/Sign up';
      loginBtn.onclick = () => window.location.href = '/login';
    }
  }
}



// Logout function
async function logoutUser() {
  try {
    await fetch('/logout', { method: 'POST' });
    window.location.reload();
  } catch (error) {
    console.error('Logout failed:', error);
    window.location.reload();
  }
}
