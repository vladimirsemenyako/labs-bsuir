interface YearSliderProps {
  min: number;
  max: number;
  value: number;
  onChange: (value: number) => void;
}

export default function YearSlider({ min, max, value, onChange }: YearSliderProps) {
  return (
    <div className="w-full">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-semibold text-white/90">Год: {value}</span>
        <span className="text-xs text-white/60">{min} - {max}</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        value={value}
        onChange={(e) => onChange(parseInt(e.target.value))}
        className="w-full h-2 rounded-full appearance-none cursor-pointer bg-white/20 accent-cyan-400"
      />
      <div className="flex justify-between text-xs text-white/60 mt-1">
        <span>{min}</span>
        <span className="font-semibold text-white">{value}</span>
        <span>{max}</span>
      </div>
    </div>
  );
}

