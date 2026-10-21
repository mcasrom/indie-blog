// src/lib/rehype-newsletter-cta.mjs
// Inserta un CTA de newsletter a mitad del artículo (tras el 2º <h2>; si no hay,
// tras el 3er párrafo). El formulario usa las clases .newsletter / .newsletter-form
// que el <script> de NewsletterForm.astro conecta con querySelectorAll, así que
// funciona sin JS extra. Se reutilizan clases ya presentes en el proyecto para que
// Tailwind las tenga generadas.

function el(tagName, properties, children = []) {
  return { type: 'element', tagName, properties, children };
}
function txt(value) {
  return { type: 'text', value };
}

const cta = el(
  'div',
  { className: ['newsletter', 'rounded-2xl', 'border', 'border-accent-300', 'bg-accent-50/50', 'p-6', 'my-8', 'dark:border-accent-700', 'dark:bg-accent-950/30'] },
  [
    el('h3', { className: ['font-serif', 'text-xl', 'font-bold', 'text-slate-900', 'dark:text-white'] }, [
      txt('📬 No te pierdas el siguiente análisis'),
    ]),
    el('p', { className: ['mt-1', 'text-sm', 'text-slate-600', 'dark:text-slate-300'] }, [
      txt('Un correo al mes con los análisis clave. Sin spam, baja cuando quieras.'),
    ]),
    el('form', { className: ['newsletter-form', 'mt-4', 'flex', 'flex-col', 'gap-2', 'sm:flex-row'], 'data-variante': 'inline' }, [
      el('input', {
        type: 'email',
        name: 'email',
        required: true,
        placeholder: 'tu@email.com',
        autocomplete: 'email',
        className: ['w-full', 'rounded-full', 'border', 'border-slate-300', 'bg-white', 'px-4', 'py-2.5', 'text-sm', 'text-slate-900', 'outline-none', 'transition', 'focus:border-accent-600', 'focus:ring-2', 'focus:ring-accent-600/30', 'dark:border-slate-700', 'dark:bg-slate-800', 'dark:text-white'],
      }, []),
      el('button', { type: 'submit', className: ['shrink-0', 'rounded-full', 'bg-accent-600', 'px-5', 'py-2.5', 'text-sm', 'font-semibold', 'text-white', 'transition', 'hover:bg-accent-700', 'dark:hover:bg-accent-500'] }, [
        txt('Suscribirme'),
      ]),
    ]),
    el('p', { className: ['newsletter-msg', 'mt-2', 'hidden', 'text-sm', 'font-medium'] }, []),
  ]
);

export default function rehypeNewsletterCta() {
  return (tree) => {
    let h2 = 0;
    let inserted = false;

    const walk = (node) => {
      if (!node || !Array.isArray(node.children)) return;
      for (let i = 0; i < node.children.length; i++) {
        const child = node.children[i];
        if (child.type === 'element' && child.tagName === 'h2') {
          h2++;
          if (!inserted && h2 === 2) {
            node.children.splice(i + 1, 0, cta);
            inserted = true;
            i++;
          }
        } else {
          walk(child);
        }
      }
    };
    walk(tree);

    if (!inserted) {
      let p = 0;
      const walkP = (node) => {
        if (!node || !Array.isArray(node.children) || inserted) return;
        for (let i = 0; i < node.children.length; i++) {
          const child = node.children[i];
          if (child.type === 'element' && child.tagName === 'p') {
            p++;
            if (p === 3) {
              node.children.splice(i + 1, 0, cta);
              inserted = true;
              return;
            }
          } else {
            walkP(child);
          }
        }
      };
      walkP(tree);
    }
  };
}
