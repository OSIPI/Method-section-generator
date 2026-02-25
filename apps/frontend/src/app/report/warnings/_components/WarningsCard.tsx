"use client";

import {useRef} from "react";
import {Card, CardTitle} from "@/components/ui/card";
import {Button} from "@/components/ui/button";
import {ClipboardCopy, Download} from "lucide-react";
import { toast } from "sonner";

const WarningsCard = ({warnings, title}: {warnings: string[], title: string}) => {

    const warningsText = warnings.join('\n');
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    const handleCopy = () => {
        if (textareaRef.current) {
            navigator.clipboard.writeText(textareaRef.current.value)
                .then(() => {
                    console.log("Errors copied to clipboard");
                })
                .catch(err => {
                    console.error("Failed to copy warnings: ", err);
                });

            toast.success("Errors copied to clipboard!");
        }
    };

    const handleDownload = () => {
        if (warningsText) {
            const blob = new Blob([warningsText], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `warnings.${title}.txt`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);

            toast.success("Errors downloaded successfully!");
        } else {
            toast.error("No warnings to download");
        }
    };

    return (
        <Card className="bg-yellow-500/5 h-full text-yellow-800 dark:text-yelow-200 p-4 relative">
            <CardTitle className="text-2xl text-foreground font-light">
                {title}
            </CardTitle>
            <div className="absolute top-2 right-2 z-10 flex gap-0.5">
                <Button
                    onClick={handleDownload}
                    size="sm"
                    variant="ghost"
                    className="hover:bg-yellow-200 dark:hover:bg-yellow-300 text-yellow-800 dark:text-yellow-200"
                    aria-label="Download warnings"
                >
                    <Download className="h-4 w-4"/>
                </Button>
                <Button
                    onClick={handleCopy}
                    size="sm"
                    variant="ghost"
                    className="hover:bg-yellow-200 dark:hover:bg-yellow-300 text-yellow-800 dark:text-yellow-200"
                    aria-label="Copy warnings to clipboard"
                >
                    <ClipboardCopy className="h-4 w-4"/>
                </Button>
            </div>

            <textarea
                ref={textareaRef}
                className="w-full h-full border-none shadow-none bg-transparent text-yellow-800 dark:text-yellow-200 resize-none"
                value={warningsText}
                readOnly
                style={{ minHeight: '100px' }}
            />
        </Card>
    );
}

export default WarningsCard;