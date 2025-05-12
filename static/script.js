$(document).ready(function () {
  $.get('/api/events', function (events) {
    if (!Array.isArray(events) || !events.length) return;

    // Get the 6 most recent events (if more than 6 events are returned)
    const recentEvents = events.slice(0, 6);

    const $slider = $('#card-slider');

    recentEvents.forEach((event) => {
      const description = event.description || 'No description available';
      const imageUrl = event.image_url || '/static/default.jpg';
      const applyLink = event.apply_link || '#';

      const $card = $(`
        <div class="card">
          <img src="${imageUrl}" alt="Event Image">
          <div class="card-body">
            <p>${description.substring(0, 100)}...</p>
            <a href="${applyLink}" target="_blank">
              <button class="apply-btn">Apply</button>
            </a>
          </div>
        </div>
      `);

      $slider.append($card);
    });

    // "See More" card
    $slider.append(`
      <div class="card see-more-card">
        <div class="card-body">
          <h3>See More</h3>
          <a href="/all-events">
            <button class="apply-btn">Browse All</button>
          </a>
        </div>
      </div>
    `);
  });
});

function scrollSlider(direction) {
  const slider = document.getElementById('card-slider');
  const scrollAmount = slider.offsetWidth * 0.8; // 80% of visible width

  slider.scrollBy({
    left: direction * scrollAmount,
    behavior: 'smooth'
  });
}

const ticker = document.getElementById("newsTicker");
const container = document.getElementById("newsContainer");
const buttons = document.querySelectorAll(".filter-buttons button");

container.addEventListener("mouseover", () => {
  ticker.style.animationPlayState = "paused";
});

container.addEventListener("mouseout", () => {
  ticker.style.animationPlayState = "running";
});

function filterNews(category) {
  const items = document.querySelectorAll(".news-item");
  buttons.forEach(btn => btn.classList.remove("active"));
  event.target.classList.add("active");
  items.forEach(item => {
    item.style.display = (category === 'all' || item.classList.contains(category)) ? 'block' : 'none';
  });
}

async function fetchNews() {
  try {
    const response = await fetch('/get-news');
    const newsItems = await response.json();
    const newsTicker = document.getElementById('newsTicker');
    newsTicker.innerHTML = '';

    newsItems.forEach(item => {
      const div = document.createElement('div');
      div.className = `news-item ${item.category.toLowerCase()}`;
      div.textContent = `📢 ${item.category.toUpperCase()}: ${item.content}`;
      newsTicker.appendChild(div);
    });
  } catch (error) {
    console.error('Error fetching news:', error);
  }
}

function filterNews(category, btn) {
  const items = document.querySelectorAll('.news-item');
  const buttons = document.querySelectorAll('.filter-buttons button');

  buttons.forEach(b => b.classList.remove('active'));
  if (btn) btn.classList.add('active');

  items.forEach(item => {
    if (category === 'all' || item.classList.contains(category)) {
      item.style.display = 'block';
    } else {
      item.style.display = 'none';
    }
  });
}

window.onload = () => {
  fetchNews().then(() => filterNews('all')); // Show all after load
};