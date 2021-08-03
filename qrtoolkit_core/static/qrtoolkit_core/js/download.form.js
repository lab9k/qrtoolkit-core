function chunk(arr, chunkSize) {
    if (chunkSize <= 0) throw "Invalid chunk size";
    const R = [];
    for (let i = 0, len = arr.length; i < len; i += chunkSize)
        R.push(arr.slice(i, i + chunkSize));
    return R;
}

window.addEventListener('DOMContentLoaded', (event) => {
    const qrImage = document.getElementById('qrExample');
    const dark = document.getElementById('id_dark');
    const light = document.getElementById('id_light');
    const scale = document.getElementById('id_scale');
    const form = document.getElementById('qr-settings-form');

    const valueChanged = () => {
        const lightValue = light.value.replace('#', '');
        const darkValue = dark.value.replace('#', '');
        const scaleValue = scale.value;
        console.log(lightValue, darkValue, scaleValue);
        qrImage.src = `http://qrcodeservice.herokuapp.com/?query=exampledata&light=${lightValue}&dark=${darkValue}&scale=${scaleValue}`;
    }

    dark.addEventListener('change', valueChanged);
    light.addEventListener('change', valueChanged);
    scale.addEventListener('change', valueChanged);
    form.addEventListener('reset', () => {
        setTimeout(valueChanged, 1);
    });

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        code_id_elems = [...document.querySelectorAll('.qrcode-id')]
            .map(el => parseInt(el.dataset.key, 10))
            .sort((a, b) => a - b);
        const chunks = chunk(code_id_elems, 50)
        for (const ch of chunks) {
            form.action = '?download=' + ch.join(',')
            const res = await fetch(form.action, {
                method: form.method,
                body: new FormData(form),
            });
            const filename = res.headers.get('Content-Disposition').split('filename=')[1]
            const blob = await res.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a); // we need to append the element to the dom -> otherwise it will not work in firefox
            a.click();
            a.remove();  //afterwards we remove the element again
        }

        // form.submit();
        return false;
    });


});
