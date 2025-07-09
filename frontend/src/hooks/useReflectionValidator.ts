// src/hooks/useReflectionValidator.ts
import { useState, useEffect } from 'react';
import { useDebounce } from './useDebounce';
import { useReflectionStore } from '../store';

interface ReflectionValidation {
    isValid: boolean;
    errors: string[];
    warnings: string[];
    wordCount: number;
    qualityScore?: number;
}

export const useReflectionValidator = (
    content: string,
    videoId: number
): ReflectionValidation => {
    const [validation, setValidation] = useState<ReflectionValidation>({
        isValid: false,
        errors: [],
        warnings: [],
        wordCount: 0,
    });

    const debouncedContent = useDebounce(content, 500);
    const { previewReflection, previewResult } = useReflectionStore();

    useEffect(() => {
        const wordCount = debouncedContent.length;
        const errors: string[] = [];
        const warnings: string[] = [];

        // 基础验证
        if (wordCount < 50) {
            errors.push('观后感内容至少需要50个字符');
        }

        if (wordCount > 2000) {
            errors.push('观后感内容不能超过2000个字符');
        }

        // 警告提示
        if (wordCount >= 50 && wordCount < 100) {
            warnings.push('建议内容更加详细，至少100字符');
        }

        if (wordCount >= 100 && !debouncedContent.includes('?') && !debouncedContent.includes('？')) {
            warnings.push('建议在观后感中提出一些思考性问题');
        }

        const isValid = errors.length === 0 && wordCount >= 50;

        setValidation({
            isValid,
            errors,
            warnings,
            wordCount,
            qualityScore: previewResult?.quality_result?.quality_score,
        });

        // 触发预检测
        if (isValid && wordCount >= 50) {
            previewReflection(debouncedContent, videoId);
        }
    }, [debouncedContent, videoId, previewReflection, previewResult]);

    return validation;
};