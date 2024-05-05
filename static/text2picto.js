
const translationContainer = document.getElementById("translation-container");
document.getElementById("text-input").spellcheck = true;

document.getElementById('clear-button').addEventListener('click', function() {
    document.getElementById('text-input').value = ''; // Clear the textarea
    // You might also want to clear the translation result
    document.getElementById('translation-container').innerHTML = '';
});

// Function to update text and translation
function updateTextAndTranslation(newText, newTranslation) {
    // Update the text input
    textInput.value = newText;

    // Update the translation display
    translationContainer.textContent = newTranslation;
}


document.addEventListener('DOMContentLoaded', function(){
    const translateButton = document.getElementById("translate-button");
    const textInput = document.getElementById("text-input");
    const hideTextCheckbox = document.getElementById('hide_text');
    const bwCheckbox = document.getElementById('bw_pictos');
    const hideInflectionCheckbox = document.getElementById('use_lemmas');
    const capitalLetterCheckbox = document.getElementById('use_upper');
    const hideArticlesCheckbox = document.getElementById('no_art');
    const hidePrepositionsCheckbox = document.getElementById('no_prep');
    const hidePunctuationsCheckbox = document.getElementById('no_punct');
    const sizeSlider = document.getElementById('size-slider');
    const spacingSlider = document.getElementById('spacing-slider');
    const printButton = document.getElementById("print-button");


    sizeSlider.addEventListener('input', function() {
        updatePictogramSize(sizeSlider.value);
    });

    spacingSlider.addEventListener('input', function() {
        console.log('Slider input event triggered.');
        updatePictogramSpacing(spacingSlider.value, translationContainer);
    });
    

    textInput.addEventListener("keyup", function(event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            translateText(textInput.value);
        }
    });

    translateButton.addEventListener("click", function() {
        translateText(textInput.value);
    });  
    
    bwCheckbox.addEventListener('change', handleBwCheckboxChange);

    function handleBwCheckboxChange() {
        if (textInput.value) {
            translateText(textInput.value);
        }
    }


    hideInflectionCheckbox.addEventListener('change', handleHideInflectionCheckboxChange);

    function handleHideInflectionCheckboxChange() {
        if (textInput.value) {
            translateText(textInput.value);
        }
    }

    capitalLetterCheckbox.addEventListener('change', function() {
        const textElements = document.querySelectorAll('.pictogram-text');
        const isUppercase = capitalLetterCheckbox.checked;
        textElements.forEach(element => {
            element.style.textTransform = isUppercase ? 'uppercase' : 'none';
        });
    });
    

    hideArticlesCheckbox.addEventListener('change', handleHideArticlesCheckboxChange);

    function handleHideArticlesCheckboxChange() {
        if (textInput.value) {
            translateText(textInput.value);
        }
    }

    hidePrepositionsCheckbox.addEventListener('change', handleHidePrepositionsCheckboxChange);

    function handleHidePrepositionsCheckboxChange() {
        if (textInput.value) {
            translateText(textInput.value);
        }
    }

    hidePunctuationsCheckbox.addEventListener('change', handleHidePunctuationsCheckboxChange);

    function handleHidePunctuationsCheckboxChange() {
        if (textInput.value) {
            translateText(textInput.value);
        }
    }

    hideTextCheckbox.addEventListener('change', function() {
        const textElements = document.querySelectorAll('.pictogram-text');
        if (hideTextCheckbox.checked) {
            textElements.forEach(el => el.classList.add('hide-text'));
        } else {
            textElements.forEach(el => el.classList.remove('hide-text'));
        }
    });


    function translateText(text) {
        const bodyData = {
            text: text, 
            use_bw: bwCheckbox.checked,
            hide_text: hideTextCheckbox.checked,
            use_lemmas: hideInflectionCheckbox.checked,
            use_upper: capitalLetterCheckbox.checked,
            no_art: hideArticlesCheckbox.checked,
            no_prep: hidePrepositionsCheckbox.checked,
            no_punct: hidePunctuationsCheckbox.checked,
        };
        // Display some loading feedback here if necessary
        fetch("translate", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(bodyData),
        })

        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Something went wrong');
            }
        })
        .then(data => {
            displayTranslations(data.translations);
        })
        .catch(error => {
            console.error('Error:', error);
        });



    
    function displayTranslations(translations) {
        translationContainer.innerHTML = ''; // Clear the container
        translations.forEach((translation, index) => {

            if (translation.line_break) {
                translationContainer.appendChild(document.createElement('br'));
            } else {
                const frame = document.createElement('div');
                frame.className = 'pictogram-frame';
     
                if (translation.no_picto) {
                    const textDiv = document.createElement('div');
                    textDiv.className = 'pictogram-text';
                    textDiv.textContent = translation.text; // Set the word as text
                    frame.appendChild(textDiv);
                } else {
                    const img = document.createElement('img');
                    img.setAttribute('data-picto-id', `picto-${index}`);
                    img.src = translation.src;
                    img.alt = translation.text || 'Pictogram';
                    frame.appendChild(img);

                    img.addEventListener('contextmenu', function(event) {
                        event.preventDefault();
                        showAlternativePictograms(translation.alternatives, event.pageX, event.pageY, `picto-${index}`);
                    });  
                }

                if (!translation.no_picto) {
                    const textLabel = document.createElement('div');
                    textLabel.className = 'pictogram-text';
                    textLabel.textContent = translation.text; // Set the word as text
                    frame.appendChild(textLabel);
                }

                translationContainer.appendChild(frame);
        }
    }); 
}



function showAlternativePictograms(alternatives, x, y, pictoId) {
    const menu = document.getElementById('context-menu');
    menu.innerHTML = ''; // Clear existing content
    
    alternatives.forEach(altSrc => {
        const img = document.createElement('img');
        img.src = altSrc;
        img.alt = 'Alternative Pictogram'; // Default alt text

        img.addEventListener('click', () => {
            replacePictogram(pictoId, img.src); 
            menu.style.display = 'none';
        });
    
        menu.appendChild(img);
    });
    
    menu.style.left = `${x}px`;
    menu.style.top = `${y}px`;
    menu.style.display = 'block';
}


function replacePictogram(pictoId, newSrc) {
    const originalPicto = document.querySelector(`img[data-picto-id="${pictoId}"]`);
    if (originalPicto) {
        originalPicto.src = newSrc;
    } else {
        console.error(`Pictogram with id ${pictoId} not found.`);
    }
}
 

document.addEventListener('click', function(event) {
    const menu = document.getElementById('context-menu');
    if (event.target.closest('#context-menu') === null) {
      menu.style.display = 'none';
    }
  });

    }

      

function updatePictogramSize(size) {
    const frames = document.querySelectorAll('.pictogram-frame');
    frames.forEach(frame => {

        frame.style.width = `${size}px`;
        frame.style.height = `${size}px`;

        const textDivs = frame.querySelectorAll('.pictogram-text');
        textDivs.forEach(textDiv =>{
            textDiv.style.fontSize = `${size * 0.14}px`;
        });
    });
}


function updatePictogramSpacing(spacing) {
    const frames = document.getElementsByClassName('pictogram-frame');
    Array.from(frames).forEach(frame => {
        frame.style.marginBottom = `${spacing}px`;
    });
} 
    


printButton.addEventListener("click", function() {
    window.print();
});

});

