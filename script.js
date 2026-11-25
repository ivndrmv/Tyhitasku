const input = document.querySelector('.search-bar input');

const algne = 'Mida soovid soodsamalt leida?';
const soovitused = ['Telefon', 'Arvuti', 'Kõrvaklapid', 'Tolmuimeja'];

const PAUS_ALGSE_TEKSTIGA = 4500;
const SOOVITUSE_KESTUS = 2500;
const HALVENEMINE = 800;

const oota = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function vaheta(tekst) {
    input.classList.add('peidus');
    await oota(HALVENEMINE);
    input.placeholder = tekst;
    input.classList.remove('peidus');
    await oota(HALVENEMINE);
}

function kasutajaTegutseb() {
    return document.activeElement === input || input.value !== '';
}

async function kaivita() {
    input.placeholder = algne;

    while (true) {
        await oota(PAUS_ALGSE_TEKSTIGA);

        for (const s of soovitused) {
            if (kasutajaTegutseb()) break;
            await vaheta(s);
            await oota(SOOVITUSE_KESTUS);
        }

        if (!kasutajaTegutseb()) {
            await vaheta(algne);
        } else {
            input.placeholder = algne;
        }
    }
}

input.addEventListener('focus', () => {
    input.classList.remove('peidus');
    input.placeholder = algne;
});

kaivita();