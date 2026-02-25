import * as React from "react"
import {cn} from "@/lib/utils"

interface CountBadgeProps {
    count: number;
    type?: "error" | "warn";
    className?: string;
}

const CountBadge = ({count, className, type}: CountBadgeProps) => {
    if (count === 0) return null;

    return (
        <span
            className={cn(
                "inline-flex items-center justify-center rounded-full min-w-[20px] h-5 px-1.5 text-xs font-medium bg-gray-200 text-black animate-pulse",
                type === "error" && "bg-red-300",
                type === "warn" && "bg-yellow-300",
                className
            )}
        >
      {count > 99 ? "99+" : count}
    </span>
    );
};

export {CountBadge};