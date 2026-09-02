import { useState } from "react";

function Header({ onSearch }) {
  const [key, setKey] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (onSearch) {
      onSearch(key.trim());
    }
  };

  return (
    <header className="bg-white/80 backdrop-blur-md sticky top-0 z-50 border-b border-slate-200/80 shadow-xs">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-3.5 flex flex-col sm:flex-row items-center justify-between gap-4">
        {/* logo */}
        <div className="flex items-center gap-3 select-none">
          <div className="w-10 h-10 rounded-xl bg-linear-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white font-black text-xl shadow-md shadow-blue-500/20">
            P
          </div>
          <div>
            <span className="text-lg font-bold text-slate-900 tracking-tight">
              Price<span className="text-blue-600">Comparator</span>
            </span>
            <p className="text-xs text-slate-600">Jumia & Expat Dakar</p>
          </div>
        </div>

        {/* barre de recherche */}
        <form
          onSubmit={handleSubmit}
          className="w-full sm:w-auto flex-1 max-w-lg flex items-center relative"
        >
          <div className="absolute left-3.5 text-slate-400 pointer-events-none">
            <svg
              className="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
          </div>
          <input
            type="text"
            placeholder="Rechercher un produit (ex: iPhone 13, TV Samsung...)"
            value={key}
            onChange={(e) => setKey(e.target.value)}
            className="w-full pl-10 pr-28 py-2.5 bg-slate-100/80 hover:bg-slate-100 focus:bg-white text-slate-800 text-sm rounded-xl border border-transparent focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 transition-all outline-none"
          />
          <button
            type="submit"
            className="absolute right-1.5 px-3.5 py-1.5 bg-blue-600 hover:bg-blue-700 active:scale-95 text-white text-xs font-medium rounded-lg shadow-sm transition-all cursor-pointer"
          >
            Rechercher
          </button>
        </form>
      </div>
    </header>
  );
}

export default Header;

