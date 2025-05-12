async function fetchNews() {
  try {
    const response = await fetch('/get-news');
    const newsItems = await response.json();

    // Define the categories and their corresponding ticker IDs
    const categories = ['fy', 'sy', 'ty', 'btech'];
    const tickers = {
      fy: document.getElementById('newsTicker-fy'),
      sy: document.getElementById('newsTicker-sy'),
      ty: document.getElementById('newsTicker-ty'),
      btech: document.getElementById('newsTicker-btech'),
    };

    // Clear existing content
    categories.forEach(cat => {
      if (tickers[cat]) tickers[cat].innerHTML = '';
    });

    // Populate news items into their respective categories
    newsItems.forEach(item => {
  const category = item.category.toLowerCase();
  if (tickers[category]) {
    const div = document.createElement('div');
    div.className = `news-item ${category}`;
    div.textContent = `📢 ${item.title}: ${item.content}`;
    tickers[category].appendChild(div);
  }
});

  } catch (error) {
    console.error('Error fetching news:', error);
  }
}

window.onload = () => {
  fetchNews();
};
