window.loadAuthors = async function() {
    try {
        const response = await fetch('/api/authors');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const authors = await response.json();
        const authorsList = document.getElementById('authors');
        authorsList.innerHTML = authors.map(author => `
            <li class="list-group-item">
                <strong>${author.name}</strong> - ${author.specialty}
                <p>${author.description}</p>
                <p>Keywords: ${author.keywords}</p>
                <p>Phrases: ${author.phrases}</p>
                <p>Text Tone: ${author.text_tone}</p>
                <button onclick="updateAuthor(${author.id})" class="btn btn-sm btn-primary">Update</button>
                <button onclick="deleteAuthor(${author.id})" class="btn btn-sm btn-danger">Delete</button>
            </li>
        `).join('');
    } catch (error) {
        console.error('Error loading authors:', error);
        alert('Error loading authors: ' + error.message);
    }
};

// Глобальные функции для обновления и удаления авторов
window.updateAuthor = async (authorId) => {
    // Implement update logic here
    alert('Update author function not implemented yet');
};

window.deleteAuthor = async (authorId) => {
    if (confirm("Are you sure you want to delete this author?")) {
        try {
            const response = await fetch(`/api/authors/${authorId}`, {
                method: 'DELETE',
            });
            if (response.ok) {
                alert('Author deleted successfully');
                await window.loadAuthors(); // Используем window.loadAuthors
            } else {
                alert('Failed to delete author');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error deleting author');
        }
    }
};

document.addEventListener('DOMContentLoaded', () => {
    const authorForm = document.getElementById('author-form');
    const loadAuthorsButton = document.getElementById('load-authors');
    const authorsList = document.getElementById('authors');

    function setupTagInput(inputId, containerId) {
        const input = document.getElementById(inputId);
        const container = document.getElementById(containerId);
        
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ',') {
                e.preventDefault();
                const tag = input.value.trim();
                if (tag) {
                    const tagElement = document.createElement('span');
                    tagElement.classList.add('tag');
                    tagElement.textContent = tag;
                    const removeButton = document.createElement('button');
                    removeButton.textContent = '×';
                    removeButton.addEventListener('click', () => {
                        container.removeChild(tagElement);
                    });
                    tagElement.appendChild(removeButton);
                    container.insertBefore(tagElement, input);
                    input.value = '';
                }
            }
        });

        return () => {
            const tags = Array.from(container.querySelectorAll('.tag')).map(tag => tag.textContent.slice(0, -1));
            return tags.join(' ') || "";
        };
    }

    const getKeywords = setupTagInput('author-keywords', 'keywords-container');
    const getPhrases = setupTagInput('author-phrases', 'phrases-container');

    authorForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const authorData = {
            name: document.getElementById('author-name').value,
            description: document.getElementById('author-description').value,
            specialty: document.getElementById('author-specialty').value,
            keywords: getKeywords(),
            phrases: getPhrases(),
            text_tone: document.getElementById('author-text-tone').value.toLowerCase() // добавьт
        };

        try {
            const response = await fetch('/api/authors', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(authorData),
            });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(JSON.stringify(errorData));
            }
            const result = await response.json();
            alert('Author profile saved successfully');
            loadAuthors();
        } catch (error) {
            console.error('Error:', error);
            alert('Error saving author profile: ' + error.message);
        }
    });

    loadAuthorsButton.addEventListener('click', window.loadAuthors);

    // Initial load of authors
    window.loadAuthors();
});

// // Global functions for updating and deleting authors
// window.updateAuthor = async (authorId) => {
//     // Implement update logic here
//     alert('Update author function not implemented yet');
// };

// window.deleteAuthor = async (authorId) => {
//     if (confirm("Are you sure you want to delete this author?")) {
//         try {
//             const response = await fetch(`/api/authors/${authorId}`, {
//                 method: 'DELETE',
//             });
//             if (response.ok) {
//                 alert('Author deleted successfully');
//                 loadAuthors();
//             } else {
//                 alert('Failed to delete author');
//             }
//         } catch (error) {
//             console.error('Error:', error);
//             alert('Error deleting author');
//         }
//     }
// };