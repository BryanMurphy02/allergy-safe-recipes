/*
 * Pagination.jsx
 *
 * Previous / Next controls for the recipe grid.
 * Displays the current page, total pages, and result range.
 *
 * Like FilterPanel, this component owns no state —
 * page and total come in as props, onPageChange goes out
 * when the user clicks a button.
 */

export default function Pagination({ page, size, total, onPageChange }) {
  const totalPages = Math.ceil(total / size);
  const from = total === 0 ? 0 : (page - 1) * size + 1;
  const to = Math.min(page * size, total);

  if (totalPages <= 1) return null;

  return (
    <div className="flex items-center justify-between mt-8 pt-6 border-t border-gray-200">

      {/* Result count */}
      <p className="text-sm text-gray-500">
        Showing <span className="font-medium text-gray-700">{from}–{to}</span> of{" "}
        <span className="font-medium text-gray-700">{total}</span> recipes
      </p>

      {/* Controls */}
      <div className="flex items-center gap-2">
        <button
          onClick={() => onPageChange(page - 1)}
          disabled={page === 1}
          className="px-3 py-1.5 text-sm font-medium rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        >
          ← Previous
        </button>

        <span className="text-sm text-gray-500 px-2">
          Page {page} of {totalPages}
        </span>

        <button
          onClick={() => onPageChange(page + 1)}
          disabled={page === totalPages}
          className="px-3 py-1.5 text-sm font-medium rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        >
          Next →
        </button>
      </div>

    </div>
  );
}