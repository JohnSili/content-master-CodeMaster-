document.addEventListener('DOMContentLoaded', () => {
    const articleForm = document.getElementById('article-form');
    const generatedArticleDiv = document.getElementById('generated-article');
    const authorSelect = document.getElementById('article-author');
    const articleActions = document.getElementById('article-actions');
    const editActions = document.getElementById('edit-actions');
    const editButton = document.getElementById('edit-article');
    const deleteButton = document.getElementById('delete-article');
    const saveButton = document.getElementById('save-article');
    const saveChangesButton = document.getElementById('save-changes');
    const discardChangesButton = document.getElementById('discard-changes');

    let currentArticle = null;
    let originalContent = '';

    async function loadAuthors() {
        try {
            const response = await fetch('/api/authors');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const authors = await response.json();
            if (authorSelect) {
                authorSelect.innerHTML = `
                    <option value="">Select an author</option>
                    ${authors.map(author => `<option value="${author.id}">${author.name}</option>`).join('')}
                `;
            }
        } catch (error) {
            console.error('Error loading authors:', error);
            alert('Error loading authors. Please try again later.');
        }
    }

    const modelSelect = document.getElementById('article-model');

    async function loadModels() {
        try {
            const response = await fetch('/api/available-models');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            if (modelSelect) {
                modelSelect.innerHTML = data.models.map(model => 
                    `<option value="${model}">${model}</option>`
                ).join('');
            }
        } catch (error) {
            console.error('Error loading models:', error);
            alert('Error loading models. Please try again later.');
        }
    }

    loadAuthors();
    loadModels();

    if (articleForm) {
        articleForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const articleData = {
                topic: document.getElementById('article-topic').value,
                length: parseInt(document.getElementById('article-length').value),
                style: document.getElementById('article-style').value,
                author_id: authorSelect ? authorSelect.value : null,
                model: modelSelect ? modelSelect.value : null  // Добавьте эту строку
            };

            try {
                console.log('Sending article data:', articleData);
                const response = await fetch('/api/generate-article', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(articleData),
                });
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(JSON.stringify(errorData));
                }
                const result = await response.json();
                console.log('Received result:', result);
                
                currentArticle = {
                    ...articleData,
                    content: result.content,
                };
                
                displayArticle(currentArticle);
                if (articleActions) articleActions.style.display = 'block';
                if (editActions) editActions.style.display = 'none';
            } catch (error) {
                console.error('Error:', error);
                alert('Error generating article: ' + error.message);
            }
        });
    }

    function displayArticle(article) {
        if (generatedArticleDiv && authorSelect) {
            const authorName = authorSelect.options[authorSelect.selectedIndex]?.text || 'Unknown Author';
            const modelName = modelSelect.options[modelSelect.selectedIndex]?.text || 'Unknown Model';  // Добавьте эту строку
            generatedArticleDiv.innerHTML = `
                <h4>${article.topic}</h4>
                <p><strong>Style:</strong> ${article.style}</p>
                <p><strong>Author:</strong> ${authorName}</p>
                <p><strong>Model:</strong> ${modelName}</p>  <!-- Добавьте эту строку -->
                <div id="article-content" class="mt-3">${article.content}</div>
            `;
        }
    }

    if (editButton) {
        editButton.addEventListener('click', () => {
            const articleContent = document.getElementById('article-content');
            if (articleContent) {
                originalContent = articleContent.innerHTML;
                articleContent.contentEditable = true;
                articleContent.focus();
            }
            if (articleActions) articleActions.style.display = 'none';
            if (editActions) editActions.style.display = 'block';
        });
    }

    if (saveChangesButton) {
        saveChangesButton.addEventListener('click', () => {
            const articleContent = document.getElementById('article-content');
            if (articleContent) {
                currentArticle.content = articleContent.innerHTML;
                articleContent.contentEditable = false;
            }
            if (articleActions) articleActions.style.display = 'block';
            if (editActions) editActions.style.display = 'none';
        });
    }

    if (discardChangesButton) {
        discardChangesButton.addEventListener('click', () => {
            const articleContent = document.getElementById('article-content');
            if (articleContent) {
                articleContent.innerHTML = originalContent;
                articleContent.contentEditable = false;
            }
            if (articleActions) articleActions.style.display = 'block';
            if (editActions) editActions.style.display = 'none';
        });
    }

    if (deleteButton) {
        deleteButton.addEventListener('click', async () => {
            if (currentArticle && confirm('Are you sure you want to discard this article?')) {
                currentArticle = null;
                if (generatedArticleDiv) generatedArticleDiv.innerHTML = '<p>Article discarded.</p>';
                if (articleActions) articleActions.style.display = 'none';
            }
        });
    }

    if (saveButton) {
        saveButton.addEventListener('click', async () => {
            if (currentArticle) {
                try {
                    const response = await fetch('/api/articles', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(currentArticle),
                    });
                    if (!response.ok) {
                        throw new Error('Failed to save article');
                    }
                    const result = await response.json();
                    alert('Article saved successfully with ID: ' + result.id);
                    currentArticle.id = result.id;
                } catch (error) {
                    console.error('Error:', error);
                    alert('Error saving article: ' + error.message);
                }
            }
        });
    }
});