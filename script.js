const api = "https://bakery-api-ag1a.onrender.com/products";

let products = [];
let allProducts = [];
let cart = [];

// LOAD PRODUCTS
function loadProducts() {
    fetch(api)
    .then(res => res.json())
    .then(data => {
        products = data;
        allProducts = data;
        renderDropdown(data);
    });
}

// DROPDOWN RENDER
function renderDropdown(data) {
    let select = document.getElementById("productSelect");
    select.innerHTML = "";

    data.forEach(p => {
        let option = document.createElement("option");
        option.value = p.id;
        option.text = p.name + " - ₹" + p.price;
        select.appendChild(option);
    });
}

// SEARCH FILTER
function filterProducts() {
    let keyword = document.getElementById("searchProduct").value.toLowerCase();

    let filtered = allProducts.filter(p =>
        p.name.toLowerCase().includes(keyword)
    );

    renderDropdown(filtered);
}

// ADD TO CART
function addToCart() {
    let id = document.getElementById("productSelect").value;
    let qty = parseInt(document.getElementById("qty").value);

    if (!qty || qty <= 0) {
        alert("Enter valid quantity");
        return;
    }

    let product = products.find(p => p.id == id);
    let existingItem = cart.find(item => item.productId == id);

    if (existingItem) {
        existingItem.qty = qty;
        existingItem.total = qty * existingItem.price;
    } else {
        cart.push({
            productId: product.id,
            name: product.name,
            price: product.price,
            qty: qty,
            total: product.price * qty
        });
    }

    displayBill();
    document.getElementById("qty").value = "";
    
}
document.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
        addToCart();
    }
});

// DISPLAY BILL
function displayBill() {
    let table = document.getElementById("billTable");
    table.innerHTML = "";

    let subtotal = 0;
    let printRows = "";

    cart.forEach((item, index) => {

        table.innerHTML += `
            <tr>
                <td>${item.name}</td>
                <td>${item.qty} × ${item.price}</td>
                <td>${item.total}</td>
                <td><button onclick="removeItem(${index})">❌</button></td>
            </tr>
        `;

        subtotal += item.total;

        printRows += `
            <tr>
                <td>${item.name}</td>
                <td>${item.qty}</td>
                <td>${item.price}</td>
                <td>${item.total}</td>
            </tr>
        `;
    });

    // ✅ FIXED GST
    let gstPercent = 5;
    let gstAmount = (subtotal * gstPercent) / 100;
    let finalTotal = subtotal + gstAmount;

    // DISPLAY (SCREEN)
    document.getElementById("subTotal").innerText = "Subtotal = ₹" + subtotal;
    document.getElementById("gstAmount").innerText = "GST (5%) = ₹" + gstAmount.toFixed(2);
    document.getElementById("grandTotal").innerText = "Total = ₹" + finalTotal.toFixed(2);

    // PRINT
    document.getElementById("printContent").innerHTML = printRows;

    document.getElementById("printSubTotal").innerText =
        "Subtotal = ₹" + subtotal;

    document.getElementById("printGST").innerText =
        "GST (5%) = ₹" + gstAmount.toFixed(2);

    document.getElementById("printTotal").innerText =
        "Total = ₹" + finalTotal.toFixed(2);

    let now = new Date();
    document.getElementById("billInfo").innerText =
        "Date: " + now.toLocaleString();
}

// REMOVE ITEM
function removeItem(index) {
    cart.splice(index, 1);
    displayBill();
}

// CLEAR BILL
function clearBill() {
    debugger;
    cart = [];
    displayBill();
    document.getElementById("searchProduct").value = "";

    filterProducts();
}

// PRINT
function printBill() {
    saveBill();
    window.print();
}

// SAVE BILL
function saveBill() {
    let total = 0;
    cart.forEach(item => total += item.total);

    fetch("http://127.0.0.1:5000/save-bill", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            total: total,
            items: cart
        })
    });
}

// NAV
function goAdd() {
    window.location.href = "add-product.html";
}
function goManage() {
    window.location.href = "manage.html";
}
function goDashboard() {
    window.location.href = "dashboard.html";
}
// function goHistory() {
//     window.location.href = "history.html";
// }

// INIT
window.onload = function () {
    loadProducts();
};
loadProducts();