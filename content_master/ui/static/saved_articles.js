document.addEventListener('DOMContentLoaded', () => {
    const savedArticlesList = document.getElementById('saved-articles-list');
    const authorFilter = document.getElementById('author-filter');
    const styleFilter = document.getElementById('style-filter');
    const articleView = document.getElementById('article-view');
    const articleTitle = document.getElementById('article-title');
    const articleAuthor = document.getElementById('article-author');
    const articleStyle = document.getElementById('article-style');
    const articleContent = document.getElementById('article-content');
    const editButton = document.getElementById('edit-button');
    const saveButton = document.getElementById('save-button');
    const deleteButton = document.getElementById('delete-button');
    const articleAnalytics = document.getElementById('article-analytics');

    let articles = [];
    let currentArticle = null;

    async function loadSavedArticles() {
        try {
            const response = await fetch('/api/articles');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            articles = await response.json();
            updateFilters();
            displaySavedArticles(articles);
        } catch (error) {
            console.error('Error loading saved articles:', error);
            alert('Error loading saved articles. Please try again later.');
        }
    }

    function updateFilters() {
        const authors = [...new Set(articles.map(a => a.author_name))];
        const styles = [...new Set(articles.map(a => a.style))];

        authorFilter.innerHTML = `<option value="">All Authors</option>` +
            authors.map(author => `<option value="${author}">${author}</option>`).join('');

        styleFilter.innerHTML = `<option value="">All Styles</option>` +
            styles.map(style => `<option value="${style}">${style}</option>`).join('');
    }

    function displaySavedArticles(articlesToDisplay) {
        savedArticlesList.innerHTML = articlesToDisplay.map(article => `
            <div class="col-md-6 mb-3">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">${article.topic}</h5>
                        <p class="card-text"><strong>Style:</strong> ${article.style}</p>
                        <p class="card-text"><strong>Author:</strong> ${article.author_name || 'Unknown'}</p>
                        <button class="btn btn-primary btn-sm view-article" data-id="${article.id}">View</button>
                    </div>
                </div>
            </div>
        `).join('');

        document.querySelectorAll('.view-article').forEach(button => {
            button.addEventListener('click', () => viewArticle(button.dataset.id));
        });
    }

    async function viewArticle(id) {
        try {
            const response = await fetch(`/api/articles/${id}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            currentArticle = await response.json();
            articleTitle.textContent = currentArticle.topic;
            articleAuthor.textContent = currentArticle.author_name || 'Unknown';
            articleStyle.textContent = currentArticle.style;
            articleContent.innerHTML = currentArticle.content;
            articleView.style.display = 'block';
            articleContent.contentEditable = false;
            editButton.style.display = 'inline-block';
            saveButton.style.display = 'none';

            // Запрос и отображение аналитики
            const analyticsResponse = await fetch(`/api/articles/${id}/analytics`);
            if (!analyticsResponse.ok) {
                throw new Error(`HTTP error! status: ${analyticsResponse.status}`);
            }
            const analytics = await analyticsResponse.json();
            displayAnalytics(analytics);
        } catch (error) {
            console.error('Error viewing article:', error);
            alert('Error viewing article. Please try again.');
        }
    }

    function displayAnalytics(analytics) {
        document.getElementById('char-count').textContent = analytics.statistics.char_count;
        document.getElementById('word-count').textContent = analytics.statistics.word_count;
        document.getElementById('sentence-count').textContent = analytics.statistics.sentence_count;
        document.getElementById('avg-word-length').textContent = analytics.statistics.average_word_length.toFixed(2);
        document.getElementById('avg-sentence-length').textContent = analytics.statistics.average_sentence_length.toFixed(2);
        document.getElementById('lexical-diversity').textContent = analytics.statistics.lexical_diversity.toFixed(2);
        document.getElementById('readability-score').textContent = analytics.statistics.readability_score.toFixed(2);
        document.getElementById('sentiment-score').textContent = analytics.statistics.sentiment_score.toFixed(2);
    
        const keyWordsList = document.getElementById('key-words-list');
        keyWordsList.innerHTML = analytics.keywords.map(([word, score]) => `
            <li class="list-group-item d-flex justify-content-between align-items-center">
                ${word}
                <span class="badge bg-primary rounded-pill">${score.toFixed(2)}</span>
            </li>
        `).join('');
    
        document.getElementById('word-cloud').src = `data:image/png;base64,${analytics.word_cloud}`;
        articleAnalytics.style.display = 'block';
    }

    editButton.addEventListener('click', () => {
        articleContent.contentEditable = true;
        articleContent.focus();
        editButton.style.display = 'none';
        saveButton.style.display = 'inline-block';
    });

    saveButton.addEventListener('click', async () => {
        try {
            const response = await fetch(`/api/articles/${currentArticle.id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ content: articleContent.innerHTML }),
            });
            if (!response.ok) {
                throw new Error('Failed to update article');
            }
            alert('Article updated successfully');
            articleContent.contentEditable = false;
            editButton.style.display = 'inline-block';
            saveButton.style.display = 'none';
            loadSavedArticles();
            viewArticle(currentArticle.id); // Обновляем аналитику после сохранения изменений
        } catch (error) {
            console.error('Error:', error);
            alert('Error updating article: ' + error.message);
        }
    });

    deleteButton.addEventListener('click', async () => {
        if (confirm('Are you sure you want to delete this article?')) {
            try {
                const response = await fetch(`/api/articles/${currentArticle.id}`, {
                    method: 'DELETE'
                });
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                alert('Article deleted successfully');
                articleView.style.display = 'none';
                articleAnalytics.style.display = 'none';
                loadSavedArticles();
            } catch (error) {
                console.error('Error deleting article:', error);
                alert('Error deleting article. Please try again.');
            }
        }
    });

    authorFilter.addEventListener('change', filterArticles);
    styleFilter.addEventListener('change', filterArticles);

    function filterArticles() {
        const authorValue = authorFilter.value;
        const styleValue = styleFilter.value;
        const filteredArticles = articles.filter(article => 
            (authorValue === '' || article.author_name === authorValue) &&
            (styleValue === '' || article.style === styleValue)
        );
        displaySavedArticles(filteredArticles);
    }

    loadSavedArticles();
});