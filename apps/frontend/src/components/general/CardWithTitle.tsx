import {cn} from "@/lib/utils";
import React from "react";

const CardWithTitle = ({children, title, className}: {
    children: React.ReactNode,
    title: string,
    className?: string
}) => {
    return (
        <div className={cn("flex flex-col gap-4", className)}>
            <h2 className={"text-2xl"}>{title}</h2>
            {children}
        </div>
    );
}

export default CardWithTitle;