let allNewsItems = []; // Store news globally after fetching

// Fetch all news and render them
async function News() {
  try {
    const response = await fetch('/get-news');
    allNewsItems = await response.json();

    const newsTicker = document.getElementById('newsTicker');
    newsTicker.innerHTML = ''; // Clear existing content

    allNewsItems.forEach(item => {
      const div = document.createElement('div');
      const category = item.category.toLowerCase();
      div.className = `news-item ${category}`;
      div.textContent = `📢 ${item.title}: ${item.content}`;
      newsTicker.appendChild(div);
    });

    filterNews('all'); // Show all by default

  } catch (error) {
    console.error('Error fetching news:', error);
  }
}

// Filter news by category
function filterNews(category, button) {
  const allItems = document.querySelectorAll('.news-item');

  allItems.forEach(item => {
    if (category === 'all' || item.classList.contains(category)) {
      item.style.display = 'block';
    } else {
      item.style.display = 'none';
    }
  });

  // Highlight the active button
  const buttons = document.querySelectorAll('.filter-buttons button');
  buttons.forEach(btn => btn.classList.remove('active'));
  if (button) button.classList.add('active');
}

window.onload = () => {
  News();
};