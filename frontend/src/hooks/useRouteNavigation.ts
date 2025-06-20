// src/hooks/useRouteNavigation.ts
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import { useCallback } from 'react';

export const useRouteNavigation = () => {
    const navigate = useNavigate();
    const params = useParams();
    const location = useLocation();

    const goToVideoList = useCallback(() => {
        navigate('/videos');
    }, [navigate]);

    const goToVideoDetail = useCallback((videoId: number) => {
        navigate(`/videos/${videoId}`);
    }, [navigate]);

    const goToReflection = useCallback((videoId: number) => {
        navigate(`/videos/${videoId}/reflection`);
    }, [navigate]);

    const goToReflectionList = useCallback(() => {
        navigate('/reflections');
    }, [navigate]);

    const goToDashboard = useCallback(() => {
        navigate('/dashboard');
    }, [navigate]);

    const goToProfile = useCallback(() => {
        navigate('/profile');
    }, [navigate]);

    const goBack = useCallback(() => {
        navigate(-1);
    }, [navigate]);

    return {
        navigate,
        params,
        location,
        goToVideoList,
        goToVideoDetail,
        goToReflection,
        goToReflectionList,
        goToDashboard,
        goToProfile,
        goBack,
    };
};