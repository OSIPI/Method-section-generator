"use client";

import {useRef} from "react";
import {Card, CardTitle} from "@/components/ui/card";
import {Button} from "@/components/ui/button";
import {ClipboardCopy, Download} from "lucide-react";
import { toast } from "sonner";

const ErrorsCard = ({errors, title}: {errors: string[], title: string}) => {
    const errorsText = errors.join('\n');
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    const handleCopy = () => {
        if (textareaRef.current) {
            navigator.clipboard.writeText(textareaRef.current.value)
                .then(() => {
                    console.log("Errors copied to clipboard");
                })
                .catch(err => {
                    console.error("Failed to copy errors: ", err);
                });

            toast.success("Errors copied to clipboard!");
        }
    };

    const handleDownload = () => {
        if (errorsText) {
            const blob = new Blob([errorsText], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `errors.${title}.txt`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            toast.success("Errors downloaded successfully!");
        } else {
            toast.error("No errors to download");
        }
    };

    return (
        <Card className="bg-red-500/5 h-full text-red-800 dark:text-red-200 p-4 relative">
            <CardTitle className="text-2xl text-foreground font-light">
                {title}
            </CardTitle>
            <div className="absolute top-2 right-2 z-10 flex gap-0.5">
                <Button
                    onClick={handleDownload}
                    size="sm"
                    variant="ghost"
                    className="hover:bg-red-200 dark:hover:bg-red-300 text-red-800 dark:text-red-200"
                    aria-label="Download errors"
                >
                    <Download className="h-4 w-4"/>
                </Button>
                <Button
                    onClick={handleCopy}
                    size="sm"
                    variant="ghost"
                    className="hover:bg-red-200 dark:hover:bg-red-300 text-red-800 dark:text-red-200"
                    aria-label="Copy errors to clipboard"
                >
                    <ClipboardCopy className="h-4 w-4"/>
                </Button>
            </div>

            <textarea
                ref={textareaRef}
                className="w-full h-full border-none shadow-none bg-transparent text-red-800 dark:text-red-200 resize-none"
                value={errorsText}
                readOnly
                style={{ minHeight: '100px' }}
            />
        </Card>
    );
}

export default ErrorsCard;