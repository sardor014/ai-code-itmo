document.getElementById('evaluation-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const resultDiv = document.getElementById('result');
    const errorDiv = document.getElementById('error');
    resultDiv.classList.add('hidden');
    errorDiv.classList.add('hidden');

    const formData = {
        floor: parseInt(document.getElementById('floor').value),
        total_floors: parseInt(document.getElementById('total_floors').value),
        rooms: parseInt(document.getElementById('rooms').value),
        total_area: parseFloat(document.getElementById('total_area').value),
        living_area: parseFloat(document.getElementById('living_area').value)
    };

    try {
        const response = await fetch('http://127.0.0.1:8000/calculate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (response.ok) {
            document.getElementById('price-per-meter').textContent = data.price_per_meter.toLocaleString();
            document.getElementById('total-price').textContent = data.total_price.toLocaleString();
            resultDiv.classList.remove('hidden');
        } else {
            let errorMsg = 'Ошибка валидации';
            if (data.detail) {
                if (Array.isArray(data.detail)) {
                    errorMsg = data.detail.map(d => d.msg).join(', ');
                } else {
                    errorMsg = data.detail;
                }
            }
            throw new Error(errorMsg);
        }
    } catch (error) {
        errorDiv.textContent = error.message;
        errorDiv.classList.remove('hidden');
    }
});
