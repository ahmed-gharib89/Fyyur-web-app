
const checkBox = document.getElementsByClassName('form-checkbox')[0]
checkBox.onchange = e => {
    const seekingDescription = document.getElementById('seeking_description');
    const labelSeekingDescription = document.getElementById('label_seeking_description');
    if (e.target.checked) {
        seekingDescription.className = 'form-control';
        labelSeekingDescription.className = '';
    }
    else {
        seekingDescription.className = 'hidden';
        labelSeekingDescription.className = 'hidden';
    }
}
